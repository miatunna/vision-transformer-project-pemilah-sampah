from flask import Flask, request, jsonify
import requests
import base64

app = Flask(__name__)

# Ganti dengan alamat server ViT Anda
PREDICT_URL = "http://127.0.0.1:5001/predict"

@app.route("/esp32_upload", methods=["POST"])
def esp32_upload():
    try:
        file = request.files.get("image")
        if not file:
            return jsonify({"error": "No image uploaded"}), 400

        # Kirim gambar ke server ViT
        response = requests.post(PREDICT_URL, files={"image": file})
        if response.status_code == 200:
            result = response.json()
            pred = result.get("prediction")
            confidence = result.get("confidence", 0)
            # Balas ke ESP32-CAM
            return jsonify({"prediction": pred, "confidence": confidence})
        else:
            return jsonify({"error": "Prediction failed"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Gunakan host 0.0.0.0 agar bisa diakses dari ESP32-CAM
    app.run(host="0.0.0.0", port=5002, debug=True)