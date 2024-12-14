export type LoanRequest = {
  person_age: number;
  person_gender: string | null;
  person_education: string | null;
  person_income: number;
  person_emp_exp: number;
  person_home_ownership: string | null;
  loan_amnt: number;
  loan_intent: string | null;
  loan_int_rate: number;
  loan_percent_income: number;
  cb_person_cred_hist_length: number;
  credit_score: number;
  previous_loan_defaults_on_file: string | null;
};

export type FormInput = {
  age: number;
  gender: string | null;
  education: string | null;
  income: number;
  empExperience: number;
  homeOwnership: string | null;
  loanAmount: number;
  loanPurpose: string | null;
  loanInterestRate: number;
  loanIncomePercentage: number;
  creditHistory: number;
  creditScore: number;
  defaultedLoans: string | null;
};

export const mapToLoanRequest = (form: FormInput): LoanRequest => {
  return {
    person_age: form.age,
    person_gender: form.gender,
    person_education: form.education,
    person_income: form.income,
    person_emp_exp: form.empExperience,
    person_home_ownership: form.homeOwnership,
    loan_amnt: form.loanAmount,
    loan_intent: form.loanPurpose,
    loan_int_rate: form.loanInterestRate,
    loan_percent_income: form.loanIncomePercentage,
    cb_person_cred_hist_length: form.creditHistory,
    credit_score: form.creditScore,
    previous_loan_defaults_on_file: form.defaultedLoans,
  };
};
