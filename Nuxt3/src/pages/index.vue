<template>
  <v-row>
    <v-col cols="1" />

    <v-col cols="8">
      <v-sheet height="95vh" class="my-6 mx-12" rounded="xl">
        <div class="d-flex flex-column ga-3 mx-6">
          <h1 class="text-center my-2">Loan approval system</h1>
          <v-form @submit.prevent v-model="formValid">
            <div class="d-flex align-center w-100 ga-3">
              <v-number-input
                v-model="form.age"
                :reverse="false"
                controlVariant="default"
                label="Age"
                :hideInput="false"
                :inset="false"
                :min="18"
                :max="150"
                :rules="ageRules"
              ></v-number-input>
              <v-radio-group
                v-model="form.gender"
                inline
                class="pl-6"
                label="Gender"
                :rules="genderRules"
              >
                <v-radio label="Male" value="male"></v-radio>
                <v-radio label="Female" value="female"></v-radio>
              </v-radio-group>
              <v-radio-group
                v-model="form.education"
                inline
                label="Highest education level"
                :rules="educationRules"
              >
                <v-radio label="High School" value="High School"></v-radio>
                <v-radio label="Associate" value="Associate"></v-radio>
                <v-radio label="Bachelor" value="Bachelor"></v-radio>
                <v-radio label="Master" value="Master"></v-radio>
                <v-radio label="Doctorate" value="Doctorate"></v-radio>
              </v-radio-group>
            </div>
            <v-number-input
              v-model="form.empExperience"
              :reverse="false"
              controlVariant="default"
              label="Years of employment experience"
              :hideInput="false"
              :inset="false"
              :min="0"
              :max="125"
              :rules="empExperienceRules"
            ></v-number-input>
            <v-radio-group
              inline
              label="Home ownership status"
              v-model="form.homeOwnership"
              :rules="homeOwnershipRules"
            >
              <v-radio label="Rent" value="RENT"></v-radio>
              <v-radio label="Mortgage" value="MORTGAGE"></v-radio>
              <v-radio label="Own" value="OWN"></v-radio>
              <v-radio label="Other" value="OTHER"></v-radio>
            </v-radio-group>
            <div class="d-flex ga-3">
              <v-number-input
                v-model="form.income"
                :reverse="false"
                controlVariant="default"
                label="Annual Income"
                :hideInput="false"
                :inset="false"
                :min="0"
                :max="9999999"
                :step="500.0"
                :rules="incomeRules"
              ></v-number-input>
              <v-number-input
                v-model="form.loanAmount"
                :reverse="false"
                controlVariant="default"
                label="Loan amount requested"
                :hideInput="false"
                :inset="false"
                :min="500.0"
                :max="50000.0"
                :step="500.0"
                :rules="loanAmountRules"
              ></v-number-input>
            </div>
            <v-radio-group
              inline
              label="Purpose of the loan"
              v-model="form.loanPurpose"
              :rules="loanPurposeRules"
            >
              <v-radio label="Education" value="EDUCATION"></v-radio>
              <v-radio label="Medical" value="MEDICAL"></v-radio>
              <v-radio label="Venture" value="VENTURE"></v-radio>
              <v-radio label="Personal" value="PERSONAL"></v-radio>
              <v-radio
                label="Debt consolidation"
                value="DEBTCONSOLIDATION"
              ></v-radio>
            </v-radio-group>
            <v-number-input
              v-model="form.loanInterestRate"
              :reverse="false"
              controlVariant="default"
              label="Loan interest rate"
              :hideInput="false"
              :inset="false"
              :min="5.0"
              :max="20.0"
              :step="0.5"
              :rules="loanInterestRateRules"
            ></v-number-input>
            <v-number-input
              v-model="form.creditHistory"
              :reverse="false"
              controlVariant="default"
              label="Length of credit history in years"
              :hideInput="false"
              :inset="false"
              :min="0"
              :max="50"
              :rules="creditHistoryRules"
            ></v-number-input>
            <v-number-input
              v-model="form.creditScore"
              :reverse="false"
              controlVariant="default"
              label="Credit score"
              :hideInput="false"
              :inset="false"
              :min="390"
              :max="850"
              :rules="creditScoreRules"
            ></v-number-input>
            <div class="d-flex align-center justify-space-between">
              <v-radio-group
                inline
                label="Defaulted on previous loans"
                v-model="form.defaultedLoans"
                :rules="defaultedLoansRules"
              >
                <v-radio label="Yes" value="Yes"></v-radio>
                <v-radio label="No" value="No"></v-radio>
              </v-radio-group>
              <v-btn
                color="green"
                size="x-large"
                type="submit"
                @click="submitForm"
                :disabled="sendBtnDisabled"
                >Send</v-btn
              >
            </div>
          </v-form>
        </div>
      </v-sheet>
    </v-col>
    <v-col cols="3">
      <v-sheet height="95vh" class="my-6 mx-12" rounded="xl">
        <h1 class="text-center mt-5">Search history</h1>
        <v-list>
          <v-list-item
            v-for="(entry, index) in searchHistory"
            :key="index"
            class="d-flex justify-space-between"
            :class="{ 'bg-red': !entry.result, 'bg-green': entry.result }"
          >
            <v-list-item-title class="d-flex justify-center w-100 align-center">
              <v-icon
                class="mr-6"
                @click="loadFormData(entry.formData)"
                color="black"
                size="32"
                >mdi-content-save</v-icon
              >{{ new Date(entry.date).toLocaleString() }}
            </v-list-item-title>
            <v-list-item-action> </v-list-item-action>
          </v-list-item>
        </v-list>
      </v-sheet>
    </v-col>
    <overlayResult @afterLeave="overlayClosed" />
  </v-row>
</template>

<script lang="ts" setup>
import { ref, watch, onMounted } from "vue";
import axios from "axios";
import { mapToLoanRequest, FormInput } from "../models/loanRequest";
import overlayResult from "../components/overlayResult.vue";
import { useAppStore } from "../stores/app";
const appStore = useAppStore();

onMounted(() => {
  searchHistory.value = getSearchHistory();
  console.log("Search history:", searchHistory.value);
});

const form = ref<FormInput>({
  age: 18,
  gender: null,
  education: null,
  income: 0,
  empExperience: 0,
  homeOwnership: null,
  loanAmount: 500.0,
  loanPurpose: null,
  loanInterestRate: 5.0,
  loanIncomePercentage: 0,
  creditHistory: 0,
  creditScore: 390,
  defaultedLoans: null,
});

watch(
  () => form.value.income,
  (newIncome) => {
    form.value.loanIncomePercentage = form.value.loanAmount / (newIncome || 1);
  }
);

watch(
  () => form.value.loanAmount,
  (newLoanAmount) => {
    form.value.loanIncomePercentage = newLoanAmount / (form.value.income || 1);
  }
);

const ageRules = [
  (v: number) => !!v || "Age is required",
  (v: number) => v >= 18 || "Age must be greater than 18",
  (v: number) => v <= 150 || "Age must be less than 150",
];
const genderRules = [(v: string) => !!v || "Gender choice is required"];
const educationRules = [
  (v: string) => !!v || "Education level choice is required",
];
const incomeRules = [
  (v: number) => (v !== null && v !== undefined) || "Income is required",
  (v: number) => v >= 0 || "Income must be greater than 0",
  (v: number) => v < 9999999 || "Income must be less than 9999999",
];
const empExperienceRules = [
  (v: number) =>
    (v !== null && v !== undefined) || "Employment experience is required",
  (v: number) => v >= 0 || "Employment experience must be greater than 0",
  (v: number) => v <= 125 || "Employment experience must be less than 125",
];
const homeOwnershipRules = [
  (v: string) => !!v || "Home ownership status is required",
];
const loanAmountRules = [
  (v: number) => !!v || "Loan amount is required",
  (v: number) => v >= 500.0 || "Loan amount must be greater than 500",
  (v: number) => v <= 50000.0 || "Loan amount must be less than 50000",
];
const loanPurposeRules = [(v: string) => !!v || "Loan purpose is required"];
const loanInterestRateRules = [
  (v: number) => !!v || "Loan interest rate is required",
  (v: number) => v >= 5.0 || "Loan interest rate must be greater than 5",
  (v: number) => v <= 20.0 || "Loan interest rate must be less than 20",
];
const creditHistoryRules = [
  (v: number) =>
    (v !== null && v !== undefined) || "Credit history is required",
  (v: number) => v >= 0 || "Credit history must be greater than 0",
  (v: number) => v <= 50 || "Credit history must be less than 50",
];
const creditScoreRules = [
  (v: number) => !!v || "Credit score is required",
  (v: number) => v >= 390 || "Credit score must be greater than 390",
  (v: number) => v <= 850 || "Credit score must be less than 850",
];
const defaultedLoansRules = [
  (v: number) => !!v || "Defaulted loans choice is required",
];

const formValid = ref(false);
const sendBtnDisabled = ref(false);

interface Response {
  prediction: number;
  probability: number[];
}
const response = ref<Response | string | null>(null);

const submitForm = async () => {
  if (!formValid.value) {
    return;
  }
  try {
    console.log("Submitting form:", form.value);
    sendBtnDisabled.value = true;
    appStore.showOverlay = true;
    appStore.overlayLoading = true;
    const loanRequest = mapToLoanRequest(form.value);
    const res = await axios.post<Response>(
      "http://localhost:8081/loan/predict",
      loanRequest
    );
    response.value = res.data;
    if (response.value.prediction === 1) {
      appStore.resultPositive = true;
    } else {
      appStore.resultNegative = true;
    }
    sendBtnDisabled.value = false;
    appStore.overlayLoading = false;
    saveSearchToHistory(form.value, response.value.prediction === 1);
  } catch (error: any) {
    console.error("Error submitting form:", error);
    response.value = error.response?.data || "An error occurred";
    appStore.resultError = true;
    sendBtnDisabled.value = false;
    appStore.overlayLoading = false;
  }
};

const overlayClosed = () => {
  console.log("Overlay closed");
  appStore.resultPositive = false;
  appStore.resultNegative = false;
  appStore.resultError = false;
  searchHistory.value = getSearchHistory();
};

const saveSearchToHistory = (formData: object, result: boolean) => {
  const historyKey = "loanSearchHistory";
  const maxHistoryLength = 15;

  const currentHistory = JSON.parse(localStorage.getItem(historyKey) || "[]");

  const newEntry = {
    formData,
    result,
    date: new Date().toISOString(),
  };

  currentHistory.unshift(newEntry);
  if (currentHistory.length > maxHistoryLength) {
    currentHistory.pop();
  }

  localStorage.setItem(historyKey, JSON.stringify(currentHistory));
};

const getSearchHistory = () => {
  const historyKey = "loanSearchHistory";
  return JSON.parse(localStorage.getItem(historyKey) || "[]");
};

const searchHistory = ref([]);
const loadFormData = (formData: object) => {
  form.value = { ...form.value, ...formData };
};
</script>
