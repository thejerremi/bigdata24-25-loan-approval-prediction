// Utilities
import { defineStore } from "pinia";

export const useAppStore = defineStore("app", {
  state: () => ({
    showOverlay: false,
    overlayLoading: false,
    resultNegative: false,
    resultPositive: false,
    resultError: false,
  }),
});
