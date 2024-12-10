import { createApp } from "vue";
import App from "./App.vue";

const app = createApp(App);
app.config.globalProperties.$apiBase = "http://127.0.0.1:5000"; // URL del backend Flask
app.mount("#app");
