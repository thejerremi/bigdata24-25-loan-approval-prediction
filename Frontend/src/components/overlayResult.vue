<template>
  <v-overlay
    class="centered-overlay"
    scrim="black"
    v-model="appStore.showOverlay"
    :persistent="closeDisabled"
    :opacity="0.99"
  >
    <div v-if="appStore.overlayLoading" class="d-flex flex-column ga-5">
      <div class="text-gold text-h1">
        Waiting for response...
        <v-progress-linear
          class="mt-12"
          color="light-blue"
          height="50"
          :model-value="progressValue"
          striped
        ></v-progress-linear>
      </div>
    </div>
    <div v-else>
      <v-card height="80vh" width="80vw">
        <v-card-text class="h-100">
          <div
            class="w-100 d-flex justify-center h-100 flex-column align-center"
          >
            <div v-if="appStore.resultPositive">
              <v-icon color="green" size="400">mdi-check-bold</v-icon>
              <h1 class="text-center mt-6">You qualify for the loan!</h1>
            </div>
            <div v-if="appStore.resultNegative">
              <v-icon color="red" size="400">mdi-close-thick</v-icon>
              <h1 class="text-center mt-6">You do not qualify for the loan.</h1>
            </div>
            <div v-if="appStore.resultError" class="text-center">
              <v-icon color="white" size="400">mdi-help</v-icon>
              <h1 class="text-center mt-6">
                An error occurred while processing your request. Please try
                again later.
              </h1>
            </div>
            <div class="text-center mt-12">
              <v-btn
                @click="appStore.showOverlay = false"
                color="white"
                size="x-large"
                >Close</v-btn
              >
            </div>
          </div>
        </v-card-text>
      </v-card>
    </div>
  </v-overlay>
</template>

<script setup>
import { storeToRefs } from "pinia";
import { ref, watch, computed, defineProps } from "vue";
import { useAppStore } from "../stores/app";
const appStore = useAppStore();
const { overlayLoading } = storeToRefs(appStore);
const closeDisabled = computed(() => appStore.overlayLoading);

const loadingValue = ref(0);

function simulateLoading() {
  if (loadingValue.value < 99) {
    loadingValue.value += Math.min(
      Math.random() * (5 - 3) + 3,
      99 - loadingValue.value
    );

    const interval = Math.random() * (20000 - 15000) + 15000;
    setTimeout(simulateLoading, interval / (99 / 5));
  }
}

watch(overlayLoading, (newValue) => {
  if (newValue) {
    loadingValue.value = 0;
    simulateLoading();
  }
});

const progressValue = computed(() => {
  return Math.min(loadingValue.value, 99).toFixed(2);
});
</script>

<style scoped>
.centered-overlay {
  display: flex;
  justify-content: center;
  align-items: center;
  background: black;
}
.scrollable-list {
  max-height: 30vh;
  overflow-y: auto;
}
</style>
