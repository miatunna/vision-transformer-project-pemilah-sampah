# Vision Transformer Sampah Klasifikasi & SPK

## Deskripsi
Aplikasi ini melakukan klasifikasi gambar sampah menggunakan Vision Transformer (ViT) dan menyediakan dashboard, riwayat, SPK (fuzzy), serta integrasi dengan ESP32-CAM.

## Struktur Project
- `app.py` : Aplikasi utama Flask (dashboard, riwayat, SPK, endpoint ESP32-CAM)
- `vit_server.py` : Server Flask untuk prediksi ViT
- `templates/` : Folder HTML template
- `static/` : Folder file statis (gambar, css, dsb)
- `classification_history.db` : Database SQLite

## Cara Menjalankan

### 1. Install Library
```bash
pip install -r requirements.txt
2. Jalankan Server ViT (Model)
Pastikan file model (vit_model_40epoch.pth) ada di folder yang sama.

3. Jalankan Aplikasi Utama Flask
4. Akses Dashboard
Buka browser ke:

atau

5. Integrasi ESP32-CAM
Pastikan ESP32-CAM mengirim gambar ke endpoint:
Komputer dan ESP32-CAM harus di jaringan WiFi yang sama.
Catatan
Jika menggunakan WeasyPrint untuk PDF, pastikan dependensi sistem (GTK, Cairo, Pango) sudah terinstall.
Untuk deployment di jaringan, pastikan port 5001 (ViT) dan 5002 (Flask utama) terbuka di firewall.
