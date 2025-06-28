import time
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# URL produk yang ditargetkan
url = 'https://www.sephora.co.id/products/dior-backstage-rosy-glow-blush/v/001-pink'

# --- BAGIAN SELENIUM UNTUK MEMUAT HALAMAN ---
print("Menginisialisasi browser dengan Selenium...")
options = webdriver.ChromeOptions()
# options.add_argument("--headless") # Hapus tanda '#' jika tidak ingin browser muncul
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

print(f"Membuka URL: {url}")
driver.get(url)

# Beri waktu 5-10 detik agar SEMUA skrip di halaman selesai dimuat
print("Menunggu 7 detik agar halaman dimuat sepenuhnya...")
time.sleep(7)

print("Mengambil source code halaman yang sudah di-render...")
# Ambil source code SETELAH JavaScript berjalan
page_source = driver.page_source

# Tutup browser karena tugasnya sudah selesai
driver.quit()
# --- AKHIR BAGIAN SELENIUM ---


# --- BAGIAN BEAUTIFULSOUP UNTUK PARSING ---
print("Mem-parsing halaman dengan BeautifulSoup...")
soup = BeautifulSoup(page_source, 'html.parser')

# Cari script tag dengan tipe 'application/ld+json'
json_ld_script = soup.find('script', {'type': 'application/ld+json'})

# Jika script ditemukan, proses datanya
if json_ld_script:
    data = json.loads(json_ld_script.string)
    
    reviews_data = data.get('review', [])
    
    if not reviews_data:
        print("JSON-LD ditemukan, tetapi tidak ada data ulasan di dalamnya.")
    else:
        list_penulis = []
        list_tanggal = []
        list_rating = []
        list_judul = []
        list_deskripsi = []
        
        for review in reviews_data:
            list_penulis.append(review.get('author'))
            list_tanggal.append(review.get('datePublished'))
            list_judul.append(review.get('name'))
            list_deskripsi.append(review.get('description'))
            
            rating_details = review.get('reviewRating', {})
            list_rating.append(rating_details.get('ratingValue'))
            
        df_reviews = pd.DataFrame({
            'penulis': list_penulis,
            'tanggal': list_tanggal,
            'rating': list_rating,
            'judul_ulasan': list_judul,
            'teks_ulasan': list_deskripsi
        })
        
        print("\nBerhasil mengambil data ulasan dari JSON-LD:")
        print(df_reviews)
        
        # Simpan ke folder data
        folder_path = 'data'
        file_name = 'ulasan_sephora_page1.csv'
        import os
        os.makedirs(folder_path, exist_ok=True)
        full_path = os.path.join(folder_path, file_name)
        df_reviews.to_csv(full_path, index=False)
        print(f"\nData berhasil disimpan ke '{full_path}'")

else:
    print("Script JSON-LD tetap tidak ditemukan bahkan setelah menggunakan Selenium.")