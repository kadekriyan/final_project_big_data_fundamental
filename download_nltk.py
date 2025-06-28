import nltk

print(">>> Memulai proses unduh paket NLTK...")
print(">>> Mengunduh 'punkt' (untuk tokenisasi)...")
nltk.download('punkt')

print(">>> Mengunduh 'stopwords' (untuk daftar kata henti)...")
nltk.download('stopwords')

print(">>> Mengunduh 'wordnet' (untuk lemmatization)...")
nltk.download('wordnet')

print(">>> Mengunduh 'vader_lexicon' (untuk analisis sentimen)...")
nltk.download('vader_lexicon')

print("\n>>> Semua paket NLTK yang dibutuhkan telah berhasil diunduh! <<<")