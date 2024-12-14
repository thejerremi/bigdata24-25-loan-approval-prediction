package com.bigdata.bigdata.Loan;

import org.springframework.kafka.requestreply.ReplyingKafkaTemplate;
import org.springframework.kafka.requestreply.RequestReplyMessageFuture;
import org.springframework.kafka.support.KafkaHeaders;
import org.springframework.messaging.Message;
import org.springframework.messaging.support.MessageBuilder;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.util.concurrent.TimeUnit;

@Service
public class LoanRequestReplyService {

    private final ReplyingKafkaTemplate<String, LoanRequest, LoanResponse> replyingKafkaTemplate;

    public LoanRequestReplyService(ReplyingKafkaTemplate<String, LoanRequest, LoanResponse> replyingKafkaTemplate) {
        this.replyingKafkaTemplate = replyingKafkaTemplate;
    }

    public LoanResponse sendLoanRequest(LoanRequest loanRequest) throws Exception {
        Message<LoanRequest> message = MessageBuilder
                .withPayload(loanRequest)
                .setHeader(KafkaHeaders.TOPIC, "loans_input")
                .build();

        RequestReplyMessageFuture<String, LoanRequest> future =
                replyingKafkaTemplate.sendAndReceive(message, Duration.ofSeconds(600));

        Message<?> responseMessage = future.get(600, TimeUnit.SECONDS);

        return (LoanResponse) responseMessage.getPayload();
    }
}
