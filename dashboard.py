import streamlit as st
import yfinance as yf
from transformers import pipeline
import pandas as pd
import plotly.express as px
import time

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Borsa Duygu Analizi", layout="wide")

st.title("🤖 Yapay Zeka Destekli Borsa Analiz Paneli")
st.markdown("Haberleri ve sosyal medya yorumlarını **FinBERT** ile analiz edip piyasa nabzını ölçüyoruz.")

# --- YAN MENÜ (SIDEBAR) ---
st.sidebar.header("Ayarlar")
hisse_kodu = st.sidebar.text_input("Hisse Kodu (Örn: AAPL, TSLA)", value="AAPL")
analiz_butonu = st.sidebar.button("Analizi Başlat 🚀")

# --- FONKSİYONLAR ---
@st.cache_resource # Modeli her seferinde yüklemesin diye belleğe alıyoruz
def model_yukle():
    return pipeline("sentiment-analysis", model="ProsusAI/finbert")

def haberleri_getir(sembol):
    try:
        hisse = yf.Ticker(sembol)
        return hisse.news
    except:
        return []

# --- ANA PROGRAM ---
if analiz_butonu:
    st.write(f"### 🔍 {hisse_kodu} İçin Veriler Toplanıyor...")
    
    # 1. Modeli Yükle (Progress Bar ile)
    with st.spinner('Yapay Zeka Beyni Yükleniyor...'):
        analizci = model_yukle()
    
    # Veri Toplama Listesi
    veriler = []
    
    # 2. Haberleri Çek
    haberler = haberleri_getir(hisse_kodu)
    if haberler:
        for haber in haberler:
            icerik = haber.get('content', {})
            baslik = icerik.get('title', 'Başlık Yok')
            if baslik != 'Başlık Yok':
                sonuc = analizci(baslik)[0]
                veriler.append({
                    "Kaynak": "Haber",
                    "İçerik": baslik,
                    "Duygu": sonuc['label'],
                    "Skor": sonuc['score']
                })
    
    # 3. Reddit Simülasyonu (Gerçek API gelene kadar)
    sahte_reddit = [
        f"{hisse_kodu} is going to the moon!",
        f"Selling my {hisse_kodu} shares, bad news.",
        f"{hisse_kodu} earnings were okay but market is weak.",
        f"I love {hisse_kodu} products, loyal customer."
    ]
    for yorum in sahte_reddit:
        sonuc = analizci(yorum)[0]
        veriler.append({
            "Kaynak": "Reddit (Simülasyon)",
            "İçerik": yorum,
            "Duygu": sonuc['label'],
            "Skor": sonuc['score']
        })
        
    # --- SONUÇLARI GÖSTERME ---
    if veriler:
        df = pd.DataFrame(veriler)
        
        # Ekranı ikiye böl (Sol: Grafikler, Sağ: Tablo)
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("📊 Duygu Dağılımı")
            # Pasta Grafiği
            fig = px.pie(df, names='Duygu', title='Genel Piyasa Havası', 
                         color='Duygu',
                         color_discrete_map={'positive':'green', 'negative':'red', 'neutral':'gray'})
            st.plotly_chart(fig, use_container_width=True)
            
            # Özet İstatistik
            pozitif_sayisi = len(df[df['Duygu'] == 'positive'])
            st.info(f"Toplam {len(df)} veri içinde {pozitif_sayisi} adet POZİTİF sinyal var.")

        with col2:
            st.subheader("📝 Detaylı Veri Listesi")
            # Tabloyu göster
            st.dataframe(df, use_container_width=True)
            
    else:
        st.error("Veri bulunamadı!")

else:
    st.info("👈 Başlamak için yandaki menüden hisse kodunu girip butona basın.")