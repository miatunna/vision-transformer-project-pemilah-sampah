#include <WiFi.h>
#include <HTTPClient.h>
#include "esp_camera.h"

// Ganti dengan SSID dan password WiFi Anda
const char* ssid = "jajajaja";
const char* password = "hahaha10";

// Ganti dengan alamat server Flask Anda
const char* serverName = "http://192.168.11.248:5001/predict";

void setup() {
  Serial.begin(115200);

  // Inisialisasi kamera (pastikan pinout sesuai board ESP32-CAM Anda)
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = 5;
  config.pin_d1 = 18;
  config.pin_d2 = 19;
  config.pin_d3 = 21;
  config.pin_d4 = 36;
  config.pin_d5 = 39;
  config.pin_d6 = 34;
  config.pin_d7 = 35;
  config.pin_xclk = 0;
  config.pin_pclk = 22;
  config.pin_vsync = 25;
  config.pin_href = 23;
  config.pin_sscb_sda = 26;
  config.pin_sscb_scl = 27;
  config.pin_pwdn = 32;
  config.pin_reset = -1;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_QVGA;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  // Inisialisasi kamera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  // Koneksi WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected!");
}

void loop() {
  // Ambil gambar
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    delay(5000);
    return;
  }

  // Kirim gambar ke server Flask
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "image/jpeg");

    int httpResponseCode = http.POST(fb->buf, fb->len);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Server response:");
      Serial.println(response);

      // Anda bisa parsing response JSON untuk mengambil hasil prediksi
      // dan menggerakkan servo sesuai kategori jika diperlukan
    } else {
      Serial.printf("Error code: %d\n", httpResponseCode);
    }
    http.end();
  }

  esp_camera_fb_return(fb);

  delay(10000); // Kirim gambar setiap 10 detik (atur sesuai kebutuhan)
}