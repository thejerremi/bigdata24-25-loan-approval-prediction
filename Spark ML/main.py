from kafka.consumer.fetcher import ConsumerRecord
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, isnan, count, struct
from pyspark.sql.types import StructType, StructField, StringType, FloatType, IntegerType
from pyspark.ml.feature import VectorAssembler, StringIndexer, StandardScaler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml import Pipeline
from kafka import KafkaProducer, KafkaConsumer
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import threading
import traceback
import os

os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.5.3,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3 main.py localhost:9092'
os.environ['JAVA_HOME'] = r'C:\jdk\jdk-11'

import findspark
findspark.init()

class LoanPredictionKafkaHandler:
    def __init__(self, bootstrap_servers=['localhost:9092'],
                 input_topic='loans_input',
                 output_topic='loans_output',
                 file_path="loan_data.csv"):

        self.spark = SparkSession.builder \
            .appName("Loan Approval Prediction with Kafka") \
            .getOrCreate()

        self.data, self.feature_columns, self.indexers, self.scaler_model, self.assembler = self._prepare_data(
            file_path)

        # trenowanie modelu
        self.model = self._train_model()

        self.bootstrap_servers = bootstrap_servers
        self.input_topic = input_topic
        self.output_topic = output_topic

        # producent wysyłający wyniki
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')  # serializacja wiadomości do formatu JSON
        )

        # konsument odbierajacy wiadomosci
        self.consumer = KafkaConsumer(
            self.input_topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id='predict-loan-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='latest'  # zaczynamy od najnowszych
        )

    def _prepare_data(self, file_path):
        data = self.spark.read.csv(file_path, header=True, inferSchema=True)

        # identyfikacja kolumn kategorycznych
        categorical_columns = [col_name for col_name in data.columns if
                               data.schema[col_name].dataType.typeName() == 'string']

        # tworzenie indeksów liczbowych dla wartości w kolumnach kategorycznych
        indexers = [
            StringIndexer(inputCol=col_name, outputCol=f"{col_name}_index", handleInvalid="keep")
            for col_name in categorical_columns
        ]

        # pomijamy loan_status
        feature_columns = [col for col in data.columns if col != 'loan_status']

        assembler = VectorAssembler(
            inputCols=[f"{col}_index" if col in categorical_columns else col for col in feature_columns],
            outputCol="features"
        )

        # skalowanie cech, aby miały podobne zakresy wartości
        scaler = StandardScaler(inputCol="features", outputCol="scaledFeatures")

        pipeline = Pipeline(stages=indexers + [assembler, scaler])

        pipeline_model = pipeline.fit(data)

        transformed_data = pipeline_model.transform(data)

        return (transformed_data,
                feature_columns,
                pipeline_model.stages[:len(indexers)],
                pipeline_model.stages[-1],
                assembler)

    def _train_model(self):
        train_data, test_data = self.data.randomSplit([0.8, 0.2], seed=42)

        lr = LogisticRegression(featuresCol="scaledFeatures", labelCol="loan_status")

        lr_model = lr.fit(train_data)

        y_pred = lr_model.transform(test_data)

        confusion_matrix = y_pred.groupBy("loan_status", "prediction").count()

        cm_df = pd.DataFrame(confusion_matrix.collect(), columns=["loan_status", "prediction", "count"])
        cm_pivot = cm_df.pivot(index="loan_status", columns="prediction", values="count").fillna(0).astype(int)

        print("Confusion Matrix (DataFrame):")
        print(cm_pivot)

        plt.figure(figsize=(8, 6))
        sns.heatmap(cm_pivot, annot=True, fmt="d", cmap="Blues", cbar=False)
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.title("Confusion Matrix")
        plt.show()

        evaluator = MulticlassClassificationEvaluator(labelCol="loan_status", predictionCol="prediction")
        accuracy = evaluator.evaluate(y_pred, {evaluator.metricName: "accuracy"})
        weighted_precision = evaluator.evaluate(y_pred, {evaluator.metricName: "weightedPrecision"})
        weighted_recall = evaluator.evaluate(y_pred, {evaluator.metricName: "weightedRecall"})
        f1_score = evaluator.evaluate(y_pred, {evaluator.metricName: "f1"})

        print(f"Accuracy: {accuracy}")
        print(f"Precision: {weighted_precision}")
        print(f"Recall: {weighted_recall}")
        print(f"F1 Score: {f1_score}")

        return lr_model

    def _preprocess_input(self, input_data):

        schema = StructType([
            StructField("person_age", FloatType(), True),
            StructField("person_gender", StringType(), True),
            StructField("person_education", StringType(), True),
            StructField("person_income", FloatType(), True),
            StructField("person_emp_exp", FloatType(), True),
            StructField("person_home_ownership", StringType(), True),
            StructField("loan_amnt", FloatType(), True),
            StructField("loan_intent", StringType(), True),
            StructField("loan_int_rate", FloatType(), True),
            StructField("loan_percent_income", FloatType(), True),
            StructField("cb_person_cred_hist_length", FloatType(), True),
            StructField("credit_score", IntegerType(), True),
            StructField("previous_loan_defaults_on_file", StringType(), True)
        ])

        df = self.spark.createDataFrame([input_data], schema=schema)

        for indexer in self.indexers:
            df = indexer.transform(df)

        df = self.assembler.transform(df)

        df = self.scaler_model.transform(df)

        return df

    def predict(self, input_data):
        try:
            df = self._preprocess_input(input_data)

            predictions = self.model.transform(df)

            first_row = predictions.select("prediction", "probability").first()

            return {
                "prediction": int(first_row['prediction']),
                "probability": first_row['probability'].tolist()
            }
        except Exception as e:
            print(f"Prediction error: {e}")
            print(traceback.format_exc())
            return {"error": str(e)}

    def start_consumer(self):
        def consume():
            for message in self.consumer:
                try:
                    # Pobierz nagłówki z wiadomości wejściowej
                    correlation_id = None
                    if isinstance(message, ConsumerRecord) and message.headers:
                        for header in message.headers:
                            if header[0] == 'kafka_correlationId':
                                correlation_id = header[1]

                    # Przetwórz wiadomość i uzyskaj predykcję
                    prediction = self.predict(message.value)

                    # Dodaj `kafka_correlationId` do wiadomości wyjściowej
                    headers = [('kafka_correlationId', correlation_id)] if correlation_id else []

                    # Wyślij odpowiedź na temat `loans_output`
                    self.producer.send(self.output_topic, value=prediction, headers=headers)
                    self.producer.flush()

                    print(f"Processed input: {message.value}")
                    print(f"Prediction: {prediction}")
                except Exception as e:
                    print(f"Error processing message: {e}")
                    print(traceback.format_exc())

        consumer_thread = threading.Thread(target=consume) # konsument w oddzielnym wątku
        consumer_thread.start()
        return consumer_thread

    def plot_feature_correlation(self):
        # Wybór kolumn liczbowych i kategorycznych
        numeric_columns = [col for col in self.feature_columns if self.data.schema[col].dataType.typeName() != 'string']
        categorical_columns = [col for col in self.feature_columns if
                               self.data.schema[col].dataType.typeName() == 'string']

        # Sprawdzenie, które kolumny kategoryczne zostały już przekształcone
        existing_columns = self.data.columns
        for col in categorical_columns:
            index_col = f"{col}_index"
            if index_col not in existing_columns:
                indexer = StringIndexer(inputCol=col, outputCol=index_col).fit(self.data)
                self.data = indexer.transform(self.data)

        # Wybór kolumn do analizy korelacji
        correlation_columns = numeric_columns + [f"{col}_index" for col in categorical_columns]

        # Przekształcenie do Pandas DataFrame
        pandas_df = self.data.select(*correlation_columns).toPandas()

        # Obliczanie korelacji
        correlation_matrix = pandas_df.corr()

        # Wizualizacja korelacji
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap="coolwarm", cbar=True)
        plt.title("Feature Correlation Matrix")
        plt.show()


if __name__ == "__main__":
    kafka_handler = LoanPredictionKafkaHandler()

    kafka_handler.plot_feature_correlation()

    consumer_thread = kafka_handler.start_consumer()

    consumer_thread.join()
