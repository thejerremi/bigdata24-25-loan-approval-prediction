package com.bigdata.bigdata.Loan;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@Data
public class LoanRequest {
    @JsonProperty("person_age")
    private float personAge;

    @JsonProperty("person_gender")
    private String personGender;

    @JsonProperty("person_education")
    private String personEducation;

    @JsonProperty("person_income")
    private float personIncome;

    @JsonProperty("person_emp_exp")
    private float personEmpExp;

    @JsonProperty("person_home_ownership")
    private String personHomeOwnership;

    @JsonProperty("loan_amnt")
    private float loanAmnt;

    @JsonProperty("loan_intent")
    private String loanIntent;

    @JsonProperty("loan_int_rate")
    private float loanIntRate;

    @JsonProperty("loan_percent_income")
    private float loanPercentIncome;

    @JsonProperty("cb_person_cred_hist_length")
    private float cbPersonCredHistLength;

    @JsonProperty("credit_score")
    private int creditScore;

    @JsonProperty("previous_loan_defaults_on_file")
    private String previousLoanDefaultsOnFile;


    public void fillDefaults() {
        if (this.personAge == 0.0) {
            this.personAge = 30;
        }
        if (this.personGender == null) {
            this.personGender = "unknown";
        }
        if (this.personEducation == null) {
            this.personEducation = "HighSchool";
        }
        if (this.personIncome == 0.0) {
            this.personIncome = 1;
        }
        if (this.personEmpExp == 0.0) {
            this.personEmpExp = 0;
        }
        if (this.personHomeOwnership == null) {
            this.personHomeOwnership = "unknown";
        }
        if (this.loanAmnt == 0.0) {
            this.loanAmnt = 1;
        }
        if (this.loanIntent == null) {
            this.loanIntent = "unknown";
        }
        if (this.loanIntRate == 0.0) {
            this.loanIntRate = 5.0F;
        }
        if (this.loanPercentIncome <= 0.0) {
            this.loanPercentIncome = (this.loanAmnt / this.personIncome);
        }
        if (this.loanPercentIncome > 0.66) {
            this.loanPercentIncome = 0.66f;
        }
        if (this.cbPersonCredHistLength == 0.0) {
            this.cbPersonCredHistLength = 0;
        }
        if (this.creditScore == 0) {
            this.creditScore = 300;
        }
        if (this.previousLoanDefaultsOnFile == null) {
            this.previousLoanDefaultsOnFile = "unknown";
        }
    }

}


