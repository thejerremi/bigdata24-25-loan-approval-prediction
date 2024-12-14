package com.bigdata.bigdata.Loan;

import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/loan")
public class LoanController {

    private final LoanRequestReplyService loanRequestReplyService;

    public LoanController(LoanRequestReplyService loanRequestReplyService) {
        this.loanRequestReplyService = loanRequestReplyService;
    }

    @CrossOrigin(origins = "http://localhost:3000")
    @PostMapping(value = "/predict", produces = MediaType.APPLICATION_JSON_VALUE)
    public LoanResponse predictLoan(@RequestBody LoanRequest loanRequest) throws Exception {
        loanRequest.fillDefaults();
        return loanRequestReplyService.sendLoanRequest(loanRequest);
    }
}

