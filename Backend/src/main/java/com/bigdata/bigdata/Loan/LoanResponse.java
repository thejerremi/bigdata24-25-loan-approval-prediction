package com.bigdata.bigdata.Loan;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

@Data
@Getter
@Setter
public class LoanResponse {
    @JsonProperty("prediction")
    private int prediction;
    @JsonProperty("probability")
    private List<Double> probability;
}

