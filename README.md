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
python [vit_server.py](http://_vscodecontentref_/1)
Pastikan file model (vit_model_40epoch.pth) ada di folder yang sama.

3. Jalankan Aplikasi Utama Flask
python [app.py](http://_vscodecontentref_/2)

4. Akses Dashboard
Buka browser ke:
http://localhost:5002/
atau
http://<IP_KOMPUTER>:5002/

5. Integrasi ESP32-CAM
Pastikan ESP32-CAM mengirim gambar ke endpoint:
http://<IP_KOMPUTER>:5002/esp32_upload
Komputer dan ESP32-CAM harus di jaringan WiFi yang sama.

Catatan
Jika menggunakan WeasyPrint untuk PDF, pastikan dependensi sistem (GTK, Cairo, Pango) sudah terinstall.
Untuk deployment di jaringan, pastikan port 5001 (ViT) dan 5002 (Flask utama) terbuka di firewall.

📁 Struktur Folder (Contoh)
vision_transformer_project/
│
├── app.py                      # Aplikasi utama Flask (dashboard, riwayat, SPK, endpoint ESP32-CAM)
├── vit_server.py               # Server Flask untuk prediksi Vision Transformer
├── requirements.txt            # Daftar library Python
├── README.md                   # Petunjuk penggunaan dan dokumentasi
├── .gitignore                  # File/folder yang diabaikan git
├── classification_history.db   # Database SQLite (otomatis dibuat)
├── vit_model_40epoch.pth       # File model Vision Transformer hasil training
│
├── templates/                  # Folder untuk file HTML (Jinja2 templates)
│   ├── index.html
│   ├── dashboard.html
│   ├── laporan_pdf.html
│   └── spk_result.html
│
├── static/                     # Folder untuk file statis (gambar, css, animasi)
│   ├── bg-trash.png
│   ├── style.css
│   └── animations/
│       ├── battery.png
│       ├── plastic.png
│       └── ... (ikon kategori lain)
│
├── dataset/                    # (Opsional) Dataset gambar sampah untuk training
│   ├── plastic/
│   ├── paper/
│   └── ... (folder kategori lain)
│
├── train_vit.ipynb             # Notebook pelatihan model Vision Transformer
├── evaluate.py                 # Skrip evaluasi model
└── esp32_server.py             # (Opsional) Server relay khusus ESP32-CAM (jika dipakai)

👨‍🎓 Kontak
Dikembangkan oleh: Miatun Nadarima
Proyek Tugas Akhir | 2025
