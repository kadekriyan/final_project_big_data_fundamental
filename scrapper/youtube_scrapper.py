import os
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tqdm import tqdm 
import time
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    print("ERROR: YOUTUBE_API_KEY tidak ditemukan. Pastikan Anda sudah membuat file .env dan mengisi variabelnya.")
    exit()
    
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

INPUT_PRODUK_CSV = 'data/product_clean.csv'
OUTPUT_KOMENTAR_CSV = 'data/youtube_reviews_raw.csv'

VIDEOS_PER_PRODUCT = 2

def search_youtube_videos(youtube_service, query, max_results=3):
    """Mencari video di YouTube berdasarkan query dan mengembalikan list video ID."""
    try:
        search_response = youtube_service.search().list(
            q=query,
            part="snippet",
            type="video",
            maxResults=max_results,
            relevanceLanguage="id" 
        ).execute()
        
        video_ids = []
        video_titles = {}
        for item in search_response.get("items", []):
            video_id = item["id"]["videoId"]
            video_title = item["snippet"]["title"]
            video_ids.append(video_id)
            video_titles[video_id] = video_title
            
        return video_ids, video_titles
    except HttpError as e:
        print(f"Error saat mencari video untuk query '{query}': {e}")
        return [], {}

def get_all_video_comments(youtube_service, video_id):
    """Mengambil semua komentar dari sebuah video ID menggunakan pagination."""
    all_comments = []
    try:
        # Request pertama
        request = youtube_service.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100, # Ambil 100 komentar per request
            textFormat="plainText"
        )
        response = request.execute()

        while response:
            for item in response["items"]:
                comment = item["snippet"]["topLevelComment"]["snippet"]
                all_comments.append({
                    'author': comment["authorDisplayName"],
                    'text': comment["textDisplay"],
                    'published_at': comment["publishedAt"],
                    'like_count': comment["likeCount"]
                })

            if "nextPageToken" in response:
                request = youtube_service.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=100,
                    textFormat="plainText",
                    pageToken=response["nextPageToken"]
                )
                response = request.execute()
            else:
                break
    except HttpError as e:
        print(f"Tidak bisa mengambil komentar untuk video {video_id}. Mungkin komentar dinonaktifkan. Error: {e}")
        
    return all_comments

def main():
    os.makedirs('data', exist_ok=True)
    
    try:
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
    except Exception as e:
        print(f"Error saat inisialisasi YouTube service: {e}")
        print("Pastikan API Key Anda valid dan YouTube Data API v3 sudah diaktifkan di Google Cloud Console.")
        return

    # Baca data produk
    try:
        df_produk = pd.read_csv(INPUT_PRODUK_CSV)
    except FileNotFoundError:
        print(f"File {INPUT_PRODUK_CSV} tidak ditemukan. Pastikan file produk sudah ada di folder 'data'.")
        return

    # Siapkan list untuk menampung semua data
    final_comments_data = []
    
    # Loop untuk setiap produk di DataFrame
    print("Memulai proses scraping komentar YouTube...")
    for index, row in tqdm(df_produk.iterrows(), total=df_produk.shape[0], desc="Mengambil Ulasan Produk"):
        product_name = row['product_name']
        product_brand = row['brand_name']
        
        search_query = f"review {product_brand} {product_name} indonesia"
        
        # Cari video relevan
        video_ids, video_titles = search_youtube_videos(youtube, search_query, max_results=VIDEOS_PER_PRODUCT)
        
        if not video_ids:
            print(f"\nTidak ada video yang ditemukan untuk: {product_name}")
            continue
            
        # Ambil komentar dari setiap video
        for video_id in video_ids:
            print(f"\nScraping komentar dari video '{video_titles[video_id]}'")
            comments = get_all_video_comments(youtube, video_id)
            
            # Tambahkan informasi produk ke setiap komentar
            for comment in comments:
                comment['product_name'] = product_name
                comment['product_brand'] = product_brand
                comment['video_title'] = video_titles[video_id]
                final_comments_data.append(comment)
            
            # Beri jeda antar video untuk menghormati API
            time.sleep(1) 

    # Simpan hasil akhir ke CSV
    if final_comments_data:
        df_final_reviews = pd.DataFrame(final_comments_data)
        df_final_reviews.to_csv(OUTPUT_KOMENTAR_CSV, index=False, encoding='utf-8-sig')
        print(f"\n\nProses Selesai! {len(final_comments_data)} komentar berhasil disimpan ke '{OUTPUT_KOMENTAR_CSV}'")
    else:
        print("\n\nProses Selesai. Tidak ada komentar yang berhasil di-scrape.")

if __name__ == "__main__":
    main()