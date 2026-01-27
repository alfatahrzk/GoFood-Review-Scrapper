import streamlit as st
import pandas as pd
import time
import random
import re
import matplotlib.pyplot as plt
import seaborn as sns
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from wordcloud import WordCloud

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="GoFood Scraper Pro",
    page_icon="🍔",
    layout="wide"
)

# --- FUNGSI UTAMA ---

# 1. Setup Driver (Versi Local/Laptop)
def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Un-comment lek pengen gak metu browser e
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# 2. Fungsi Normalisasi Teks
def clean_text(text):
    norm_dict = {
        "gak": "tidak", "ga": "tidak", "g": "tidak", "nggak": "tidak",
        "yg": "yang", "bgt": "banget", "bgtt": "banget",
        "bs": "bisa", "bisaa": "bisa", "dgn": "dengan", "dr": "dari",
        "kalo": "kalau", "kl": "kalau", "jd": "jadi", "krn": "karena",
        "utk": "untuk", "tp": "tapi", "sy": "saya", "aku": "saya",
        "sdh": "sudah", "dah": "sudah", "blm": "belum",
        "thx": "terima kasih", "makasih": "terima kasih",
        "uenak": "enak", "uenaaak": "enak", "enak": "enak",
        "mantul": "mantap", "pesen": "pesan",
        "lama": "lama", "tumpah": "tumpah", "dingin": "dingin",
        "mentah": "mentah", "asin": "asin"
    }
    
    if not isinstance(text, str): return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    words = text.split()
    words = [norm_dict.get(w, w) for w in words]
    return " ".join(words)

# 3. Fungsi Load More
def load_more_reviews(driver, max_clicks):
    status_text = st.empty() 
    count = 0
    btn_selector = (By.XPATH, "//button[.//span[text()='Load more']]")

    while count < max_clicks:
        try:
            load_more_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(btn_selector)
            )
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", load_more_btn)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", load_more_btn)
            count += 1
            status_text.info(f"⏳ Sedang memuat... (Klik ke-{count})")
            time.sleep(random.uniform(2, 3))
        except:
            status_text.success(f"✅ Selesai! Tombol 'Load More' sudah tidak ada atau batas tercapai ({count} klik).")
            break
    return count

# 4. Fungsi Scraper Inti
def scrape_data(driver):
    all_reviews = []
    cards = driver.find_elements(By.XPATH, "//div[./div[contains(@class, 'flex items-center')]]")
    
    progress_bar = st.progress(0)
    total_cards = len(cards)
    
    for i, card in enumerate(cards):
        try:
            def get_text_safe(parent, method, selector):
                try:
                    found = parent.find_elements(method, selector)
                    if found: return found[0].text.strip()
                    return None
                except: return None

            name = get_text_safe(card, By.TAG_NAME, 'h3')
            rating_text = get_text_safe(card, By.XPATH, ".//div[contains(@class, 'text-gf-content-primary')]//span")
            review = get_text_safe(card, By.CSS_SELECTOR, 'p.gf-body-m')
            items = get_text_safe(card, By.XPATH, ".//span[contains(@class, 'break-words') and contains(@class, 'ml-2')]")
            raw_date = get_text_safe(card, By.XPATH, ".//div[contains(text(), 'Purchased on')]")
            purchase_date = raw_date.replace('Purchased on ', '') if raw_date else None
            user_since = get_text_safe(card, By.XPATH, ".//span[contains(text(), 'Gojek user since')]")

            try:
                rating = float(rating_text) if rating_text else None
            except:
                rating = None

            if name or rating:
                all_reviews.append({
                    'name': name,
                    'rating': rating,
                    'review': review,
                    'items_ordered': items,
                    'purchase_date': purchase_date,
                    'user_since': user_since
                })
        except:
            continue
        
        if total_cards > 0:
            progress_bar.progress(min((i + 1) / total_cards, 1.0))
            
    return pd.DataFrame(all_reviews)

# --- UI STREAMLIT ---

st.title("🕵️‍♂️ GoFood Review Scraper Pro (Local)")
st.markdown("Aplikasi scraping ulasan GoFood dengan fitur **Analisis Sentimen & Menu Terlaris**.")

# SIDEBAR PENGATURAN
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    target_url = st.text_input("Link Resto GoFood:", placeholder="https://gofood.co.id/...")
    
    st.subheader("Opsi Pengambilan Data")
    mode_scrape = st.radio(
        "Pilih Metode:",
        ("Batasi Jumlah (Cepat)", "Ambil SEMUA Ulasan (Lama)")
    )
    
    if mode_scrape == "Batasi Jumlah (Cepat)":
        max_clicks = st.slider("Maksimal Klik 'Load More':", 5, 50, 10)
    else:
        max_clicks = 10000 
        st.warning("⚠️ Mode ini akan berjalan terus sampai tombol 'Load More' hilang.")

    st.divider()
    start_btn = st.button("Mulai Scraping 🚀", type="primary")

# LOGIC EKSEKUSI
if start_btn and target_url:
    st.divider()
    
    with st.spinner("Membuka browser..."):
        driver = setup_driver()
        
    try:
        driver.get(target_url)
        
        # --- UPDATE 1: AMBIL NAMA & TAMPILKAN DI UI ---
        try:
            # Cara 1: Tembak langsung H1 sing duwe class 'gf-heading-xl' (Sesuai temuanmu)
            resto_name_real = driver.find_element(By.CSS_SELECTOR, "h1.gf-heading-xl").text
        except:
            try:
                # Cara 2: Tembak H1 sembarang (Cadangan)
                resto_name_real = driver.find_element(By.TAG_NAME, "h1").text
            except: 
                # Cara 3: Lek gagal kabeh, jupuk Title Browser
                resto_name_real = driver.title

        # Tampilkan Pesan Sukses Terkoneksi
        st.success(f"✅ Terkoneksi ke: **{resto_name_real}**")
        st.info("Sedang memuat ulasan, mohon tunggu sebentar...")
        # ---------------------------------------------
        
        # Siapkan nama file
        clean_name = re.sub(r'[\\/*?:"<>|]', "", resto_name_real).replace(" ", "_")
        st.session_state['resto_filename'] = f"Review_{clean_name}.csv"
        
        # Proses Load More
        load_more_reviews(driver, max_clicks)
        
        st.text("Mengekstrak data dari halaman...")
        df = scrape_data(driver)
        driver.quit()
        
        if not df.empty:
            # Cleaning Duplikat
            df = df.sort_values(by=['review'], na_position='last')
            df = df.drop_duplicates(subset=['name', 'user_since'], keep='first')
            
            # --- UPDATE 2: NAMBAH KOLOM NAMA RESTO DI CSV ---
            # Nambah kolom 'restaurant_name' ing ngarep dhewe utawa mburi
            df['restaurant_name'] = resto_name_real
            
            # Pindah kolom 'restaurant_name' dadi kolom pertama (Opsional, ben rapi)
            cols = ['restaurant_name'] + [c for c in df.columns if c != 'restaurant_name']
            df = df[cols]
            # ------------------------------------------------
            
            st.session_state['data_hasil'] = df
            st.success(f"Selesai! Berhasil mengambil {len(df)} data.")
        else:
            st.error("Gagal mengambil data. Pastikan link benar.")
            
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        if 'driver' in locals(): driver.quit()

# TAMPILKAN DASHBOARD
if 'data_hasil' in st.session_state:
    df = st.session_state['data_hasil']
    nama_file_download = st.session_state.get('resto_filename', 'gofood_data.csv')
    
    st.divider()
    st.header(f"📊 Analisis: {df['restaurant_name'].iloc[0]}")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rating Rata-rata", f"{df['rating'].mean():.2f} ⭐")
    c2.metric("Total Review", len(df))
    c3.metric("Review Teks", df['review'].notna().sum())
    
    c4.download_button(
        f"📥 Download CSV",
        df.to_csv(index=False).encode('utf-8'),
        nama_file_download,
        "text/csv"
    )
    
    tab1, tab2, tab3, tab4 = st.tabs(["Grafik Rating", "🏆 Top Menu", "Word Cloud", "Tabel Data"])
    
    with tab1:
        colA, colB = st.columns(2)
        with colA:
            st.subheader("Distribusi Bintang")
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.countplot(x='rating', data=df, palette='viridis', ax=ax)
            st.pyplot(fig)
        with colB:
            st.subheader("Sentimen (Berdasarkan Rating)")
            def kat(r): return 'Positif' if r>=4 else ('Netral' if r==3 else 'Negatif')
            df['kategori'] = df['rating'].apply(kat)
            fig2, ax2 = plt.subplots()
            df['kategori'].value_counts().plot.pie(autopct='%1.1f%%', ax=ax2, colors=['#99ff99','#ffff99','#ff9999'])
            ax2.set_ylabel('')
            st.pyplot(fig2)

    with tab2:
        st.subheader("Menu Paling Laris")
        if 'items_ordered' in df.columns and df['items_ordered'].notna().sum() > 0:
            items_series = df['items_ordered'].dropna()
            all_items = items_series.str.split(' - ').explode()
            top_items = all_items.value_counts().head(10)
            
            fig_menu, ax_menu = plt.subplots(figsize=(10, 6))
            sns.barplot(y=top_items.index, x=top_items.values, palette='rocket', ax=ax_menu)
            ax_menu.set_xlabel("Frekuensi Dipesan")
            st.pyplot(fig_menu)
        else:
            st.warning("⚠️ Data menu tidak ditemukan.")

    with tab3:
        st.subheader("Kata Paling Sering Muncul")
        all_text = " ".join(df['review'].dropna().apply(clean_text))
        stopwords = set(['yang', 'dan', 'di', 'ke', 'ini', 'itu', 'nya', 'untuk', 'dengan', 'dari', 'karena', 'kalau', 'tapi', 'saya', 'makan', 'makanan', 'pesan', 'beli', 'kak', 'min'])
        
        if len(all_text) > 10:
            wc = WordCloud(width=800, height=400, background_color='white', stopwords=stopwords, colormap='magma').generate(all_text)
            fig_wc, ax_wc = plt.subplots(figsize=(10, 5))
            ax_wc.imshow(wc, interpolation='bilinear')
            ax_wc.axis('off')
            st.pyplot(fig_wc)
        else:
            st.warning("Data teks tidak cukup untuk membuat Word Cloud.")

    with tab4:
        st.dataframe(df)