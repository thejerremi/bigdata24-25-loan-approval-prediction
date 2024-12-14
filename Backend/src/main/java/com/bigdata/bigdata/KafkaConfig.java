package com.bigdata.bigdata;

import com.bigdata.bigdata.Loan.LoanRequest;
import com.bigdata.bigdata.Loan.LoanResponse;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.config.ConcurrentKafkaListenerContainerFactory;
import org.springframework.kafka.core.*;
import org.springframework.kafka.listener.ConcurrentMessageListenerContainer;
import org.springframework.kafka.requestreply.ReplyingKafkaTemplate;
import org.springframework.kafka.support.serializer.ErrorHandlingDeserializer;
import org.springframework.kafka.support.serializer.JsonDeserializer;
import org.springframework.kafka.support.serializer.JsonSerializer;

import java.util.HashMap;
import java.util.Map;

/**
 * Kafka configuration class that sets up producers, consumers, and a ReplyingKafkaTemplate
 * for handling request-reply communication between Kafka topics.
 */
@Configuration
public class KafkaConfig {

    /**
     * Creates a ReplyingKafkaTemplate to handle request-reply semantics in Kafka.
     *
     * @param producerFactory the factory to create Kafka producers.
     * @param containerFactory the factory to create Kafka listener containers for replies.
     * @return a configured ReplyingKafkaTemplate.
     */
    @Bean
    public ReplyingKafkaTemplate<String, LoanRequest, LoanResponse> replyingKafkaTemplate(
            ProducerFactory<String, LoanRequest> producerFactory,
            ConcurrentKafkaListenerContainerFactory<String, LoanResponse> containerFactory) {

        // Creates a message listener container for the 'loans_output' topic.
        ConcurrentMessageListenerContainer<String, LoanResponse> replyContainer =
                containerFactory.createContainer("loans_output");
        replyContainer.getContainerProperties().setGroupId("predict-loan-group");

        // Configures the ReplyingKafkaTemplate with the producer and reply container.
        ReplyingKafkaTemplate<String, LoanRequest, LoanResponse> template =
                new ReplyingKafkaTemplate<>(producerFactory, replyContainer);
        template.setSharedReplyTopic(true);
        return template;
    }

    /**
     * Configures a Kafka ProducerFactory for serializing keys as strings and values as LoanRequest objects.
     *
     * @return a configured ProducerFactory.
     */
    @Bean
    public ProducerFactory<String, LoanRequest> producerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, JsonSerializer.class);
        return new DefaultKafkaProducerFactory<>(props);
    }

    /**
     * Configures a Kafka ConsumerFactory for deserializing keys as strings and values as LoanResponse objects.
     *
     * @return a configured ConsumerFactory.
     */
    @Bean
    public ConsumerFactory<String, LoanResponse> consumerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, ErrorHandlingDeserializer.class);
        props.put(ErrorHandlingDeserializer.VALUE_DESERIALIZER_CLASS, JsonDeserializer.class);
        props.put(JsonDeserializer.TRUSTED_PACKAGES, "com.bigdata.bigdata.Loan");

        // Configures the consumer to use an ErrorHandlingDeserializer for LoanResponse.
        return new DefaultKafkaConsumerFactory<>(props,
                new StringDeserializer(),
                new ErrorHandlingDeserializer<>(new JsonDeserializer<>(LoanResponse.class)));
    }

    /**
     * Configures a KafkaListenerContainerFactory to manage Kafka consumer containers.
     *
     * @return a configured ConcurrentKafkaListenerContainerFactory.
     */
    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, LoanResponse> kafkaListenerContainerFactory() {
        ConcurrentKafkaListenerContainerFactory<String, LoanResponse> factory =
                new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(consumerFactory());
        return factory;
    }
}
