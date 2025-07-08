import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter

st.set_page_config(layout="wide")
st.title('Dashboard Analisis Sentimen Produk Sephora')
st.markdown("Menganalisis ulasan YouTube untuk menjawab **'MENGAPA'** di balik sentimen pelanggan.")

@st.cache_data
def load_data(path):
    try:
        df = pd.read_csv(path)
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        df['loves_count'] = pd.to_numeric(df['loves_count'], errors='coerce')
        return df
    except FileNotFoundError:
        st.error(f"File tidak ditemukan di path: {path}. Pastikan 'dataset_final.csv' sudah ada.")
        return None

def generate_product_summary(df_product_reviews):
    positive_reviews = df_product_reviews[df_product_reviews['sentimen'] == 'Positif']['comment_clean'].dropna()
    negative_reviews = df_product_reviews[df_product_reviews['sentimen'] == 'Negatif']['comment_clean'].dropna()
    pos_words = " ".join(positive_reviews).split()
    neg_words = " ".join(negative_reviews).split()
    pos_word_counts = Counter(pos_words).most_common(5)
    neg_word_counts = Counter(neg_words).most_common(5)
    
    if pos_word_counts:
        top_pos_keywords = ", ".join([f"**{word}**" for word, count in pos_word_counts])
        plus_point = f"👍 **Kelebihan Utama:** Pelanggan sangat menyukai produk ini karena aspek terkait: {top_pos_keywords}. Kata-kata ini sering muncul dalam ulasan positif, menunjukkan kepuasan pada area tersebut."
    else:
        plus_point = "👍 **Kelebihan Utama:** Tidak cukup data ulasan positif untuk disimpulkan."

    if neg_word_counts:
        top_neg_keywords = ", ".join([f"**{word}**" for word, count in neg_word_counts])
        minus_point = f"👎 **Area Perbaikan:** Beberapa keluhan atau area yang perlu diperhatikan berpusat pada: {top_neg_keywords}. Ini adalah kata kunci yang paling sering muncul di ulasan negatif."
    else:
        minus_point = "👎 **Area Perbaikan:** Tidak ada keluhan signifikan yang ditemukan dari ulasan."
        
    num_pos = len(positive_reviews)
    num_neg = len(negative_reviews)
    if num_pos > num_neg * 2 and num_pos > 5:
        conclusion = "✅ **Kesimpulan Produk:** Secara keseluruhan, produk ini diterima dengan sangat baik oleh pasar. Kelebihannya jauh lebih menonjol daripada kekurangannya, menjadikannya produk yang sangat direkomendasikan berdasarkan suara pelanggan."
    elif num_neg > num_pos and num_neg > 3:
        conclusion = "⚠️ **Kesimpulan Produk:** Produk ini tampaknya memiliki beberapa masalah yang perlu perhatian serius. Jumlah ulasan negatif yang signifikan, yang berpusat pada kata kunci di atas, menunjukkan adanya ruang besar untuk perbaikan agar dapat memenuhi ekspektasi pelanggan."
    else:
        conclusion = "⚖️ **Kesimpulan Produk:** Produk ini mendapatkan respon yang beragam. Meskipun memiliki beberapa kelebihan yang diakui, ada juga beberapa kekurangan yang perlu dipertimbangkan baik oleh calon pembeli maupun oleh tim produk untuk perbaikan di masa depan."
        
    return plus_point, minus_point, conclusion

df = load_data('data/dataset_final.csv')

if df is not None:
    st.sidebar.header('⚙️ Filter Analisis')
    
    all_brands = sorted(df['brand_name'].unique())
    selected_brand = st.sidebar.selectbox(
        'Langkah 1: Pilih Brand',
        options=all_brands
    )
    
    df_brand_filtered = df[df['brand_name'] == selected_brand]
    
    all_products = sorted(df_brand_filtered['product_name'].unique())
    selected_product = st.sidebar.selectbox(
        'Langkah 2: Pilih Produk',
        options=all_products
    )

    st.sidebar.markdown("---")
    st.sidebar.info("Pilih brand lalu produk di atas untuk melihat analisis mendalam.")

    st.header(f"Analisis Mendalam untuk: {selected_product}")
    
    df_product_filtered = df_brand_filtered[df_brand_filtered['product_name'] == selected_product]

    st.subheader("📝 Ringkasan Otomatis dari Ulasan")
    
    if not df_product_filtered.empty and df_product_filtered['comment_clean'].notna().any():
        plus_point, minus_point, conclusion = generate_product_summary(df_product_filtered)
        st.markdown(plus_point)
        st.markdown(minus_point)
        st.markdown("---")
        st.markdown(conclusion)
    else:
        st.warning("Tidak ada data ulasan yang cukup untuk produk ini.")

    st.markdown("---")

    st.subheader("📊 Visualisasi Pendukung")
    col1, col2, col3 = st.columns(3) 
    with col1:
        st.write("**Distribusi Sentimen**")
        sentiment_counts = df_product_filtered['sentimen'].value_counts()
        st.bar_chart(sentiment_counts)

    with col2:
        st.write("**Word Cloud Ulasan Positif**")
        positif_text = " ".join(review for review in df_product_filtered[df_product_filtered['sentimen'] == 'Positif']['comment_clean'].dropna())
        if positif_text:
            wordcloud_pos = WordCloud(width=400, height=300, background_color="white", colormap="Greens").generate(positif_text)
            fig, ax = plt.subplots()
            ax.imshow(wordcloud_pos, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.write("Tidak ada ulasan positif.")

    with col3: 
        st.write("**Word Cloud Ulasan Negatif**")
        negatif_text = " ".join(review for review in df_product_filtered[df_product_filtered['sentimen'] == 'Negatif']['comment_clean'].dropna())
        if negatif_text:
            wordcloud_neg = WordCloud(width=400, height=300, background_color="white", colormap="Reds").generate(negatif_text)
            fig, ax = plt.subplots()
            ax.imshow(wordcloud_neg, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.write("Tidak ada ulasan negatif.")
            
    st.write("**Top 10 Kata yang Paling Sering Muncul dalam Ulasan Negatif**")
    negatif_text_for_barchart = " ".join(review for review in df_product_filtered[df_product_filtered['sentimen'] == 'Negatif']['comment_clean'].dropna())
    if negatif_text_for_barchart:
        neg_words = negatif_text_for_barchart.split()
        neg_word_counts = Counter(neg_words).most_common(10)
        df_neg_words = pd.DataFrame(neg_word_counts, columns=['Kata Kunci', 'Jumlah'])
        st.bar_chart(df_neg_words.set_index('Kata Kunci'))
    else:
        st.write("Tidak ada data untuk ditampilkan.")

    st.markdown("---")
    st.subheader("💬 Telusuri Ulasan Asli")
    st.dataframe(df_product_filtered[['sentimen', 'text']].rename(columns={'text': 'Teks Asli Komentar'}), height=300)

    st.markdown("---")
    st.header("Kesimpulan Umum Proyek")
    st.success("""
    Proyek ini menunjukkan kekuatan penggabungan data terstruktur (produk) dan tidak terstruktur (ulasan) untuk menghasilkan wawasan yang mendalam. 
    Dengan menganalisis 'suara pelanggan' secara langsung dari YouTube, kita dapat memahami **alasan di balik angka rating**, mengidentifikasi kekuatan spesifik, dan menemukan area perbaikan untuk setiap produk. 
    Dashboard ini berfungsi sebagai alat bantu pengambilan keputusan berbasis data, memungkinkan strategi produk dan pemasaran yang lebih tajam dan responsif terhadap kebutuhan pasar.
    """)