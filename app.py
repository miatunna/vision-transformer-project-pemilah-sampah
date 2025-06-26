from flask import Flask, render_template, request, jsonify, make_response
import requests
from PIL import Image
import io
import torch
from collections import defaultdict
import base64
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///classification_history.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# URL ke server Flask prediksi
PREDICT_URL = "http://127.0.0.1:5001/predict"

detection_stats = defaultdict(int)
classification_history = []

class ClassificationHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50))
    confidence = db.Column(db.Float)
    image = db.Column(db.Text)
    datetime = db.Column(db.String(25))
    volume = db.Column(db.Integer)  # volume sampah (misal: 0-100)
    danger = db.Column(db.Integer)  # tingkat bahaya (1-10)

class SPKResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), unique=True)
    danger = db.Column(db.Integer)
    priority = db.Column(db.String(20))
    total_count = db.Column(db.Integer)
    pickup_time = db.Column(db.String(20))
    updated_at = db.Column(db.String(25))

CATEGORY_DANGER = {
    "battery": 10,
    "plastic": 7,
    "paper": 1,
    "metal": 7,
    "biological": 4,
    "brown-glass": 8,
    "cardboard": 5,
    "green-glass": 8,
    "white-glass": 8,
    "clothes": 5,
    "shoes": 6,
    "trash": 9}

@app.route("/", methods=["GET", "POST"])
def index():
    print("Route '/' accessed")
    print(f"Request method: {request.method}")
    if request.method == "POST":
        if "image" not in request.files:
            return render_template("index.html", error="No image file uploaded.")

        file = request.files["image"]
        if file.filename == "":
            return render_template("index.html", error="No file selected.")

        # Simpan gambar ke base64 untuk preview
        img_bytes = file.read()
        img_b64 = "data:image/jpeg;base64," + base64.b64encode(img_bytes).decode()
        file.seek(0)  # Reset pointer agar file bisa dikirim ke server prediksi

        # Kirim gambar ke server prediksi
        try:
            response = requests.post(PREDICT_URL, files={"image": file})
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.text}")
            if response.status_code == 200:
                result = response.json()
                pred = result.get("prediction")
                if pred:
                    detection_stats[pred] += 1
                    # Contoh: volume bisa didapat dari input user atau deteksi model (sementara random/manual)
                    volume = int(request.form.get("volume", 50))  # default 50 jika tidak ada input
                    danger = CATEGORY_DANGER.get(pred, 1)

                    new_entry = ClassificationHistory(
                        category=pred,
                        confidence=result.get("confidence") or 0,
                        image=img_b64,
                        datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        volume=volume,
                        danger=danger
                    )
                    db.session.add(new_entry)
                    db.session.commit()
                    update_spk_results()  # <-- Tambahkan baris ini setelah commit data baru
                return render_template(
                    "index.html",
                    prediction=pred,
                    confidence=result.get("confidence"),
                    predicted_image=img_b64
                )
            else:
                return render_template("index.html", error="Prediction failed.")
        except Exception as e:
            print(f"Error: {e}")
            return render_template("index.html", error=f"Error: {e}")
    
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def predict():
    print("Request received:", request.files)
    if 'image' not in request.files:
        return jsonify({'error': 'No image file'}), 400

    file = request.files['image']
    try:
        image = Image.open(io.BytesIO(file.read())).convert('RGB')
        input_tensor = transform(image).unsqueeze(0).to(device)

        with torch.no_grad():
            output = model(input_tensor)
            logits = output.logits if hasattr(output, 'logits') else output
            pred_idx = logits.argmax(dim=1).item()
            pred_label = class_names[pred_idx]
            # Tambahkan confidence
            probs = torch.softmax(logits, dim=1)
            confidence = probs[0, pred_idx].item()

        # Simpan riwayat klasifikasi
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        classification_history.append({
            'timestamp': timestamp,
            'label': pred_label,
            'confidence': confidence
        })

        return jsonify({'prediction': pred_label, 'confidence': confidence})
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/dashboard")
def dashboard():
    rows = ClassificationHistory.query.order_by(ClassificationHistory.datetime.desc()).all()
    category_counts = get_category_counts()
    dashboard_data = []
    stats = {}
    for row in rows:
        total_category_count = category_counts.get(row.category, 0)
        prioritas, waktu = fuzzy_priority(row.volume, row.danger, total_category_count)
        dashboard_data.append({
            "category": row.category,
            "volume": row.volume,
            "danger": row.danger,
            "prioritas": prioritas,
            "waktu": waktu,
            "datetime": row.datetime,
            "jumlah_sampah": total_category_count
        })
        stats[row.category] = stats.get(row.category, 0) + 1
    return render_template("dashboard.html", dashboard_data=dashboard_data, stats=stats)

@app.route("/history")
def history():
    q = request.args.get("q", "").lower()
    sort = request.args.get("sort", "desc")
    query = ClassificationHistory.query
    if q:
        query = query.filter(ClassificationHistory.category.ilike(f"%{q}%"))
    if sort == "desc":
        query = query.order_by(ClassificationHistory.datetime.desc())
    else:
        query = query.order_by(ClassificationHistory.datetime.asc())
    history = query.all()
    return render_template("history.html", history=history, q=q, sort=sort)

@app.route("/delete_all_history", methods=["POST"])
def delete_all_history():
    try:
        num_rows_deleted = db.session.query(ClassificationHistory).delete()
        db.session.commit()
        return jsonify({"success": True, "deleted": num_rows_deleted})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/spk_result")
def spk_result():
    results = SPKResult.query.order_by(SPKResult.category).all()
    return render_template("spk_result.html", results=results)

@app.route("/cetak_laporan", methods=["GET", "POST"])
def cetak_laporan():
    from io import StringIO
    import csv

    # Ambil data statistik & hasil SPK
    rows = ClassificationHistory.query.order_by(ClassificationHistory.datetime.desc()).all()
    spk_results = SPKResult.query.order_by(SPKResult.category).all()
    tanggal_laporan = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Siapkan CSV di memori
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["LAPORAN STATISTIK & HASIL SPK SAMPAH"])
    writer.writerow([f"Tanggal Laporan: {tanggal_laporan}"])
    writer.writerow([])

    # Statistik Klasifikasi
    writer.writerow(["Statistik Klasifikasi Sampah"])
    writer.writerow(["Waktu", "Kategori", "Confidence", "Volume", "Bahaya"])
    for row in rows:
        writer.writerow([row.datetime, row.category, row.confidence, row.volume, row.danger])
    writer.writerow([])

    # Hasil SPK
    writer.writerow(["Hasil SPK Prioritas Sampah"])
    writer.writerow(["Kategori", "Bahaya", "Prioritas", "Jumlah Total", "Waktu Pengangkutan", "Update Terakhir"])
    for item in spk_results:
        writer.writerow([item.category, item.danger, item.priority, item.total_count, item.pickup_time, item.updated_at])

    # Buat response download
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename=laporan_sampah_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    response.headers["Content-type"] = "text/csv"

    # Hapus data setelah laporan dicetak
    db.session.query(ClassificationHistory).delete()
    db.session.query(SPKResult).delete()
    db.session.commit()

    return response


def fuzzy_priority(volume, danger, total_category_count):
    # volume: 0-10, danger: 1-10, total_category_count: int
    # Aturan fuzzy sederhana dengan tambahan jumlah sampah kategori
    if volume is None or danger is None:
        return "Tidak diketahui", "Ditunda"
    # Jika jumlah sampah kategori sudah banyak, naikkan prioritas
    if danger >= 8 or volume >= 8 or total_category_count >= 10:
        return "Tinggi", "Sekarang"
    elif danger >= 4 or volume >= 4 or total_category_count >= 5:
        return "Sedang", "Besok"
    else:
        return "Rendah", "Ditunda"

def get_category_counts():
    # Menghitung jumlah entri (sampah) per kategori
    counts = {}
    for row in ClassificationHistory.query.all():
        counts[row.category] = counts.get(row.category, 0) + 1
    return counts

def update_spk_results():
    from sqlalchemy.exc import IntegrityError
    # Hitung jumlah sampah per kategori
    counts = {}
    for row in ClassificationHistory.query.all():
        counts[row.category] = counts.get(row.category, 0) + 1

    for category in CATEGORY_DANGER.keys():
        danger = CATEGORY_DANGER[category]
        total = counts.get(category, 0)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if total == 0:
            priority, pickup = "Tidak perlu diangkut", "Tidak perlu diangkut"
        elif danger >= 8 or total >= 8:
            priority, pickup = "Tinggi", "Sekarang"
        elif danger >= 4 or total >= 4:
            priority, pickup = "Sedang", "Besok"
        else:
            priority, pickup = "Rendah", "Ditunda"

        # Cek apakah sudah ada, update atau insert
        spk = SPKResult.query.filter_by(category=category).first()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if spk:
            spk.danger = danger
            spk.priority = priority
            spk.total_count = total
            spk.pickup_time = pickup
            spk.updated_at = now
        else:
            spk = SPKResult(
                category=category,
                danger=danger,
                priority=priority,
                total_count=total,
                pickup_time=pickup,
                updated_at=now
            )
            db.session.add(spk)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

@app.route("/esp32_upload", methods=["POST"])
def esp32_upload():
    try:
        # Ambil gambar dari ESP32-CAM
        file = request.files.get("image")
        if not file:
            return jsonify({"error": "No image uploaded"}), 400

        # Simpan gambar ke base64 (opsional, untuk riwayat)
        img_bytes = file.read()
        img_b64 = "data:image/jpeg;base64," + base64.b64encode(img_bytes).decode()
        file.seek(0)

        # Kirim ke server prediksi
        response = requests.post(PREDICT_URL, files={"image": file})
        if response.status_code == 200:
            result = response.json()
            pred = result.get("prediction")
            confidence = result.get("confidence", 0)
            volume = 5  # Bisa diatur sesuai kebutuhan
            danger = CATEGORY_DANGER.get(pred, 1)

            # Simpan ke database
            new_entry = ClassificationHistory(
                category=pred,
                confidence=confidence,
                image=img_b64,
                datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                volume=volume,
                danger=danger
            )
            db.session.add(new_entry)
            db.session.commit()
            update_spk_results()

            # Kirim hasil ke ESP32-CAM
            return jsonify({"prediction": pred, "confidence": confidence})
        else:
            return jsonify({"error": "Prediction failed"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

with app.app_context():
    db.create_all()
    update_spk_results()

if __name__ == "__main__":
    #app.run(debug=True)
    app.run(host="0.0.0.0", port=5002, debug=True)