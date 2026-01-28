import streamlit as st
import pandas as pd
import time
import random
import re
import pickle # Kanggo load model
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
    page_title="GoReview Analytics",
    page_icon="🤖",
    layout="wide"
)

# --- 1. SETUP MODEL AI & CLEANING ---

# Load Model sing wis dilatih
@st.cache_resource
def load_model():
    try:
        with open('maestro-model.pkl', 'rb') as f:
            model = pickle.load(f)
        return model
    except Exception as e:
        return None

model = load_model()

# Kamus Alay (Kudu padha karo pas training)
slang_dict = {
    "gak": "tidak", "ga": "tidak", "g": "tidak", "nggak": "tidak", "gk": "tidak",
    "yg": "yang", "bgt": "banget", "bgtt": "banget",
    "bs": "bisa", "bisaa": "bisa", "dgn": "dengan", "dr": "dari",
    "kalo": "kalau", "kl": "kalau", "jd": "jadi", "krn": "karena",
    "utk": "untuk", "tp": "tapi", "sy": "saya", "aku": "saya", "gw": "saya",
    "sdh": "sudah", "dah": "sudah", "blm": "belum",
    "thx": "terima kasih", "makasih": "terima kasih", "tks": "terima kasih",
    "uenak": "enak", "uenaaak": "enak", "enak": "enak",
    "mantul": "mantap", "mantap": "bagus", "best": "bagus", "good": "bagus",
    "bad": "buruk", "parah": "buruk", "kecewa": "buruk",
    "pesen": "pesan", "order": "pesan"
}

def bersihkan_teks(text):
    if not isinstance(text, str): return ""
    text = text.lower()
    text = re.sub(r'[^a-z\s]', ' ', text)
    words = text.split()
    words = [slang_dict.get(w, w) for w in words]
    return " ".join(words)

# --- 2. SETUP DRIVER (LOCAL) ---
def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Un-comment lek pengen mode hantu
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# --- 3. FUNGSI SCRAPING ---
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
            status_text.success(f"✅ Load selesai! ({count} klik).")
            break
    return count

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

# --- UI UTAMA ---

st.title("🤖 GoReview Analytics (Powered by Maestro Model)")
st.markdown("Scraping ulasan + Analisis Sentimen Cerdas (Hybrid SVM).")

# Sidebar
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    target_url = st.text_input("Link Resto GoFood:", placeholder="https://gofood.co.id/...")
    
    st.subheader("Opsi Scraping")
    mode_scrape = st.radio("Metode:", ("Cepat (Limit)", "Deep Dive (Semua)"))
    
    if mode_scrape == "Cepat (Limit)":
        max_clicks = st.slider("Max Load More:", 5, 50, 10)
    else:
        max_clicks = 10000 
        st.warning("⚠️ Mode ini akan berjalan lama!")
        
    st.divider()
    
    # Status Model
    if model:
        st.success("🧠 Otak AI Siap!")
    else:
        st.error("⚠️ Model 'model_sentimen_hybrid.pkl' tidak ditemukan! Pastikan file ada di folder yang sama.")
        
    start_btn = st.button("Mulai Analisis 🚀", type="primary")

# Logic Utama
if start_btn and target_url:
    st.divider()
    
    with st.spinner("Membuka browser..."):
        driver = setup_driver()
        
    try:
        driver.get(target_url)
        
        try:
            resto_name_real = driver.find_element(By.CSS_SELECTOR, "h1.gf-heading-xl").text
        except:
            resto_name_real = driver.title 

        st.success(f"✅ Terkoneksi ke: **{resto_name_real}**")
        
        # Nama file
        clean_name = re.sub(r'[\\/*?:"<>|]', "", resto_name_real).replace(" ", "_")
        st.session_state['resto_filename'] = f"Analisis_{clean_name}.csv"
        
        load_more_reviews(driver, max_clicks)
        
        st.text("Mengekstrak & Menganalisis data...")
        df = scrape_data(driver)
        driver.quit()
        
        if not df.empty:
            # Cleaning Data
            df = df.sort_values(by=['review'], na_position='last')
            df = df.drop_duplicates(subset=['name', 'user_since'], keep='first')
            df['restaurant_name'] = resto_name_real
            
            # --- BAGIAN PENTING: AI PREDICTION ---
            if model:
                # 1. Bersihkan teks dhisik (sama kayak pas training)
                df['review_clean'] = df['review'].apply(bersihkan_teks)
                
                # 2. Prediksi (Lek reviewne kosong, anggep Netral/Positif wae utawa skip)
                # Kita mung prediksi sing ana review tekse
                df_pred = df[df['review_clean'] != ""].copy()
                
                if not df_pred.empty:
                    prediksi = model.predict(df_pred['review_clean'])
                    df_pred['prediksi_sentimen'] = prediksi # 1: Positif, 0: Negatif
                    
                    # Gabungne balik nang df utama
                    df = df.merge(df_pred[['review', 'prediksi_sentimen']], on='review', how='left')
                    
                    # Mapping 0/1 dadi Teks
                    df['label_ai'] = df['prediksi_sentimen'].apply(lambda x: 'Positif 😊' if x == 1 else ('Negatif 😡' if x == 0 else 'Netral/No Text'))
                else:
                    df['label_ai'] = 'No Text'
            # -------------------------------------
            
            st.session_state['data_hasil'] = df
            st.success(f"Selesai! {len(df)} data berhasil dianalisis.")
        else:
            st.error("Gagal mengambil data.")
            
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        if 'driver' in locals(): driver.quit()

# DASHBOARD
if 'data_hasil' in st.session_state:
    df = st.session_state['data_hasil']
    
    st.divider()
    st.header(f"📊 Laporan AI: {df['restaurant_name'].iloc[0]}")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rating Asli", f"{df['rating'].mean():.2f} ⭐")
    c2.metric("Total Review", len(df))
    
    # Hitung Sentimen AI
    if 'label_ai' in df.columns:
        pos = len(df[df['label_ai'] == 'Positif 😊'])
        neg = len(df[df['label_ai'] == 'Negatif 😡'])
        c3.metric("Sentimen Positif", f"{pos} User")
        c3.metric("Sentimen Negatif", f"{neg} User") # Tampil double metric biar keren
    
    c4.download_button(
        f"📥 Download Laporan",
        df.to_csv(index=False).encode('utf-8'),
        st.session_state.get('resto_filename', 'data.csv'),
        "text/csv"
    )
    
    tab1, tab2, tab3, tab4 = st.tabs(["🧠 AI vs Bintang", "🏆 Top Menu", "☁️ Word Cloud", "📋 Data Lengkap"])
    
    with tab1:
        colA, colB = st.columns(2)
        with colA:
            st.subheader("Apa Kata Bintang? (Rating Asli)")
            fig, ax = plt.subplots()
            sns.countplot(x='rating', data=df, palette='viridis', ax=ax)
            st.pyplot(fig)
            
        with colB:
            st.subheader("Apa Kata AI? (Analisis Teks)")
            if 'label_ai' in df.columns:
                # Filter sing No Text
                df_chart = df[df['label_ai'] != 'Netral/No Text']
                fig2, ax2 = plt.subplots()
                colors = {'Positif 😊': '#2ecc71', 'Negatif 😡': '#e74c3c'}
                df_chart['label_ai'].value_counts().plot.pie(autopct='%1.1f%%', ax=ax2, colors=[colors.get(x, '#999') for x in df_chart['label_ai'].value_counts().index])
                ax2.set_ylabel('')
                st.pyplot(fig2)
            else:
                st.info("Model belum aktif.")

    with tab2:
        st.subheader("Menu Paling Laris")
        if 'items_ordered' in df.columns and df['items_ordered'].notna().sum() > 0:
            items_series = df['items_ordered'].dropna()
            all_items = items_series.str.split(' - ').explode()
            top_items = all_items.value_counts().head(10)
            fig_menu, ax_menu = plt.subplots(figsize=(8,5))
            sns.barplot(y=top_items.index, x=top_items.values, palette='rocket', ax=ax_menu)
            st.pyplot(fig_menu)
        else:
            st.warning("Data menu tidak ditemukan.")

    with tab3:
        st.subheader("Kata Kunci Keluhan vs Pujian")
        
        col_pos, col_neg = st.columns(2)
        stopwords = set(['yang', 'dan', 'di', 'ke', 'ini', 'itu', 'nya', 'untuk', 'dengan', 'dari', 'karena', 'kalau', 'tapi', 'saya', 'makan', 'makanan', 'pesan', 'beli', 'kak', 'min', 'bgt', 'banget', 'gak', 'tidak'])
        
        with col_pos:
            st.info("👍 Kata-kata di Review POSITIF")
            if 'label_ai' in df.columns:
                text_pos = " ".join(df[df['label_ai']=='Positif 😊']['review_clean'].astype(str))
                if len(text_pos) > 10:
                    wc = WordCloud(width=400, height=300, background_color='white', stopwords=stopwords, colormap='Greens').generate(text_pos)
                    fig_wc, ax_wc = plt.subplots()
                    ax_wc.imshow(wc)
                    ax_wc.axis('off')
                    st.pyplot(fig_wc)
        
        with col_neg:
            st.error("👎 Kata-kata di Review NEGATIF")
            if 'label_ai' in df.columns:
                text_neg = " ".join(df[df['label_ai']=='Negatif 😡']['review_clean'].astype(str))
                if len(text_neg) > 10:
                    wc = WordCloud(width=400, height=300, background_color='white', stopwords=stopwords, colormap='Reds').generate(text_neg)
                    fig_wc, ax_wc = plt.subplots()
                    ax_wc.imshow(wc)
                    ax_wc.axis('off')
                    st.pyplot(fig_wc)

    with tab4:
        st.dataframe(df)