import requests

url = "http://127.0.0.1:5000/predict"
image_path = "C:\\Users\\mnada\\Documents\\vision_transformer_project\\tes\\IMG_20250425_152530_240.jpg"

with open(image_path, "rb") as image_file:
    response = requests.post(url, files={"image": image_file})

# Cetak status kode HTTP
print(f"Status code: {response.status_code}")

# Cetak respons JSON jika tersedia
try:
    print(response.json())
except Exception as e:
    print(f"Error parsing JSON: {e}")
    print(response.text)