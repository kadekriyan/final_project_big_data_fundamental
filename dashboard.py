import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# PENGATURAN HALAMAN & JUDUL 
# Mengatur layout halaman menjadi lebar dan memberikan judul
st.set_page_config(layout="wide")
st.title('Dashboard Analisis Sentimen Produk Sephora dari Ulasan YouTube')
st.markdown("Dashboard ini menganalisis ulasan produk dari YouTube untuk mendapatkan insight tentang sentimen pelanggan.")

# FUNGSI UNTUK MEMUAT DATA
# @st.cache_data digunakan agar Streamlit tidak perlu memuat ulang data setiap kali ada interaksi
@st.cache_data
def load_data(path):
    try:
        df = pd.read_csv(path)
        # Konversi kolom penting ke tipe data yang benar, paksa error menjadi NaN
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        df['loves_count'] = pd.to_numeric(df['loves_count'], errors='coerce')
        return df
    except FileNotFoundError:
        st.error(f"File tidak ditemukan di path: {path}. Pastikan Anda sudah menjalankan skrip analisis utama untuk menghasilkan 'dataset_final.csv'.")
        return None

# MUAT DATA
# Muat dataset final yang sudah berisi sentimen
df = load_data('data/dataset_final.csv')

# Jika data berhasil dimuat, tampilkan dashboard. Jika tidak, hentikan eksekusi.
if df is not None:

    # SIDEBAR UNTUK FILTER
    st.sidebar.header('⚙️ Filter Data')
    
    # Filter berdasarkan Brand (pilih beberapa)
    all_brands = df['brand_name'].unique()
    selected_brands = st.sidebar.multiselect(
        'Pilih Brand:',
        options=all_brands,
        default=all_brands[:3] # Default: tampilkan 3 brand pertama
    )
    
    # Filter DataFrame utama berdasarkan pilihan di sidebar
    if selected_brands:
        df_filtered = df[df['brand_name'].isin(selected_brands)]
    else:
        df_filtered = df.copy() # Jika tidak ada yang dipilih, tampilkan semua

    # TAMPILAN UTAMA (MAIN PANEL)

    # Membuat 3 kolom untuk menampilkan metrik utama (KPI)
    st.header('Ringkasan Utama')
    col1, col2, col3 = st.columns(3)
    
    total_reviews = df_filtered['comment_clean'].count()
    avg_rating = df_filtered['rating'].mean()
    avg_loves = df_filtered['loves_count'].mean()

    col1.metric("Total Ulasan YouTube", f"{total_reviews:,}")
    col2.metric("Rata-rata Rating Produk", f"{avg_rating:.2f} ⭐" if avg_rating > 0 else "N/A")
    col3.metric("Rata-rata Loves Count", f"{avg_loves:,.0f} ❤️" if avg_loves > 0 else "N/A")

    st.markdown("---")

    # Membuat 2 kolom untuk visualisasi sentimen dan produk
    st.header('Analisis Sentimen & Produk')
    col_sentimen, col_produk = st.columns(2)

    with col_sentimen:
        st.subheader('Distribusi Sentimen')
        sentiment_counts = df_filtered['sentimen'].value_counts()
        st.bar_chart(sentiment_counts)

    with col_produk:
        st.subheader('Top 5 Produk Berdasarkan Loves Count')
        # Menghapus duplikat produk agar loves_count tidak dihitung berulang kali
        top_products = df_filtered.drop_duplicates(subset=['product_name']).nlargest(5, 'loves_count')
        st.bar_chart(top_products.set_index('product_name')['loves_count'])

    st.markdown("---")
    
    # Membuat 2 kolom untuk Word Cloud
    st.header('Kata Kunci Populer dalam Ulasan')
    col_pos, col_neg = st.columns(2)

    with col_pos:
        st.subheader('Ulasan Positif')
        # Gabungkan semua teks ulasan positif menjadi satu string besar
        positif_text = " ".join(review for review in df_filtered[df_filtered['sentimen'] == 'Positif']['comment_clean'].dropna())
        if positif_text:
            wordcloud_pos = WordCloud(width=800, height=400, background_color="white", colormap="Greens").generate(positif_text)
            fig, ax = plt.subplots()
            ax.imshow(wordcloud_pos, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.write("Tidak ada ulasan positif untuk ditampilkan.")

    with col_neg:
        st.subheader('Ulasan Negatif')
        negatif_text = " ".join(review for review in df_filtered[df_filtered['sentimen'] == 'Negatif']['comment_clean'].dropna())
        if negatif_text:
            wordcloud_neg = WordCloud(width=800, height=400, background_color="white", colormap="Reds").generate(negatif_text)
            fig, ax = plt.subplots()
            ax.imshow(wordcloud_neg, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.write("Tidak ada ulasan negatif untuk ditampilkan.")

    st.markdown("---")

    # Menampilkan tabel data yang bisa dieksplorasi
    st.header('Telusuri Data Ulasan')
    st.dataframe(df_filtered[['brand_name', 'product_name', 'sentimen', 'text']].rename(columns={'text': 'Teks Asli Komentar'}))