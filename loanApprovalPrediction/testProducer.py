from kafka import KafkaProducer
import json
import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.5.3,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3 main.py localhost:9092'
os.environ['JAVA_HOME'] = r'C:\jdk\jdk-11'
import findspark
findspark.init()
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

message = [
    {
        "person_age": 22.0,
        "person_gender": "female",
        "person_education": "Master",
        "person_income": 71948.0,
        "person_emp_exp": 0.0,
        "person_home_ownership": "RENT",
        "loan_amnt": 35000.0,
        "loan_intent": "PERSONAL",
        "loan_int_rate": 16.02,
        "loan_percent_income": 0.49,
        "cb_person_cred_hist_length": 3.0,
        "credit_score": 561,
        "previous_loan_defaults_on_file": "No"
    }
]

producer.send('loans_input', message)
producer.flush()
print("wysłano")
