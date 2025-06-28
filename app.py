import pandas as pd
import re
import os

df = pd.read_csv("data/product_info.csv")

# lihat informasi dasar dan 5 baris pertama
print(df.info())
print(df.head())

# standarisasi kolom brand_name menjadi string lowercase semua
df["brand_name"] = df["brand_name"].str.lower()
print(f"jumlah brand uniq setelah dibersihkan : {df['brand_name'].unique()}")

# Menangani nilai kosong pada metrik numerik
df["loves_count"].fillna(0, inplace=True)
df["reviews"].fillna(0, inplace=True)

# isi nilai null pada ratinf dengan nilai median
median_rating = df["rating"].median()
df["rating"].fillna(median_rating, inplace=True)

# cek tipe data sudah benar
df["loves_count"] = df["loves_count"].astype(int)
df["reviews"] = df["reviews"].astype(int)
df["rating"] = df["rating"].astype(float)

print("Nilai kosong pada matrik sudah diatasi")


def extract_size_in_ml(size_text):
    if not isinstance(size_text, str):
        return None

    ml_match = re.search(r"(\d+(\.\d+)?)\s*mL", size_text, re.IGNORECASE)
    if ml_match:
        return float(ml_match.group(1))

    oz_match = re.search(r"(\d+(\.\d+)?)\s*oz", size_text, re.IGNORECASE)
    if oz_match:
        oz_value = float(oz_match.group(1))
        return oz_value * 29.5735  # 1 oz = 29.5735 mL

    return None


df["size_ml"] = df["size"].apply(extract_size_in_ml)
# print(df[["size", "size_ml"]].head(100))

median_size_ml = df["size_ml"].median()
df["size_ml"].fillna(median_size_ml, inplace=True)

print(df[["size", "size_ml"]].head(100))

# bersihkan kolom variasi
# Mengisi nilai null pada kolom variasi
df["variation_type"].fillna("Tidak Ada", inplace=True)
df["variation_value"].fillna("Tidak Ada", inplace=True)

print("Nilai kosong pada kolom variasi sudah diatasi.")

print("\n--- INFO DATASET SETELAH DIBERSIHKAN ---")
print(df.info())

print("\n--- CEK ULANG NILAI KOSONG ---")
print(df.isnull().sum())

# Simpan DataFrame yang sudah bersih ke file CSV baru
folder_path = "data"
file_name = "product_clean.csv"

os.makedirs(folder_path, exist_ok=True)

full_path = os.path.join(folder_path, file_name)

df.to_csv(full_path, index=False)
print(f"\nDataset yang sudah bersih berhasil disimpan ke '{full_path}'")
