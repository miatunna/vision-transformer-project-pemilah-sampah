import torch
import os

model_path = "vit_model.pth"

# Periksa apakah file ada
if not os.path.exists(model_path):
    print(f"File {model_path} tidak ditemukan.")
else:
    try:
        state_dict = torch.load(model_path, map_location="cpu")
        print(f"Tipe data yang dimuat: {type(state_dict)}")

        # Jika state_dict adalah dictionary, tampilkan kunci-kuncinya
        if isinstance(state_dict, dict):
            print("Keys in state_dict:", state_dict.keys())
        else:
            print("File ini bukan state dictionary.")
    except Exception as e:
        print(f"Terjadi error saat memuat file: {e}")