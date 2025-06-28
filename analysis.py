import pandas as pd
import re
import nltk
import os

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer

print("--- Memulai Skrip Analisis Data ---")

# MEMUAT DATA MENTAH 
print("1. Memuat dataset produk dan ulasan...")
try:
    df_produk = pd.read_csv('data/product_clean.csv')
    df_ulasan = pd.read_csv('data/youtube_reviews_raw.csv')

    # KODE DIAGNOSIS 
    print("\n--- Cek Nama Kolom ---")
    print("Kolom di df_produk:", df_produk.columns.tolist())
    print("Kolom di df_ulasan:", df_ulasan.columns.tolist())
    print("------------------------\n")
except: 
    print('File dataset tidak tersedia')

# Cek & unduh paket NLTK jika belum ada
try:
    nltk.data.find('corpora/wordnet')
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('sentiment/vader_lexicon')
    print("   -> Paket NLTK sudah lengkap.")
except LookupError:
    print("   -> Beberapa paket NLTK tidak ditemukan. Mengunduh...")
    nltk.download(['punkt', 'stopwords', 'wordnet', 'vader_lexicon'], quiet=True)
    print("   -> Unduhan selesai.")

# Inisialisasi alat-alat dari NLTK
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = word_tokenize(text) 
    cleaned_tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    return " ".join(cleaned_tokens)

df_ulasan['comment_clean'] = df_ulasan['text'].apply(preprocess_text)
print("   -> Preprocessing teks selesai.")


# MENGGABUNGKAN DATA 
print("3. Menyamakan nama kolom & menggabungkan data...")

# Ganti nama kolom 'product_brand' di df_ulasan menjadi 'brand_name'
df_ulasan.rename(columns={'product_brand': 'brand_name'}, inplace=True)

# Sekarang kedua DataFrame punya kolom 'brand_name' yang sama
# Lakukan merge dengan kunci yang sudah konsisten
df_final = pd.merge(df_produk, df_ulasan, on=['product_name', 'brand_name'], how='left')

print("   -> Penggabungan data selesai.")


# ANALISIS SENTIMEN 
print("4. Membersihkan kolom teks final sebelum analisis sentimen...")
df_final['comment_clean'] = df_final['comment_clean'].astype(str).fillna('')
print("   -> Kolom 'comment_clean' sekarang dijamin 100% string.")

print("5. Melakukan analisis sentimen...")
sia = SentimentIntensityAnalyzer()
def get_sentiment(text):
    score = sia.polarity_scores(text)['compound']
    if score > 0.05:
        return 'Positif'
    elif score < -0.05:
        return 'Negatif'
    else:
        return 'Netral'

df_final['sentimen'] = df_final['comment_clean'].apply(get_sentiment)
print("   -> Analisis sentimen selesai.")


# MENYIMPAN HASIL AKHIR
print("6. Menyimpan dataset final...")
output_path = 'data/dataset_final.csv'
df_final.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"--- Skrip Selesai. Dataset final berhasil disimpan di '{output_path}' ---")