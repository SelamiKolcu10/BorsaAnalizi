import streamlit as st
import yfinance as yf
from transformers import pipeline
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="AI Borsa Terminali", layout="wide")

st.title("🤖 Yapay Zeka Destekli Borsa Terminali")
st.info("Ayarları aşağıdan yapıp **'Analizi Başlat'** butonuna basın.")

# --- SESSION STATE ---
if 'analiz_aktif' not in st.session_state:
    st.session_state.analiz_aktif = False

# --- AYARLAR ---
col1, col2, col3 = st.columns(3)

with col1:
    hisse_girdisi = st.text_input("Hisse Kodları (Örn: AAPL, TSLA)", value="AAPL, TSLA")

with col2:
    zaman_secimi = st.selectbox("Analiz Periyodu", ("1 Gün", "1 Hafta", "1 Ay", "3 Ay", "1 Yıl", "5 Yıl"))

with col3:
    st.write("") 
    st.write("") 
    analiz_butonu = st.button("Analizi Başlat 🚀", use_container_width=True, type="primary")

sma_aktif = st.checkbox("Hareketli Ortalamayı Göster (SMA 50)", value=True)

# Zaman haritası
periyot_map = {
    "1 Gün": ("1d", "15m"), "1 Hafta": ("5d", "60m"), 
    "1 Ay": ("1mo", "1d"), "3 Ay": ("3mo", "1d"), 
    "1 Yıl": ("1y", "1d"), "5 Yıl": ("5y", "1wk")
}
secilen_periyot, secilen_aralik = periyot_map.get(zaman_secimi, ("1y", "1d"))

if analiz_butonu:
    st.session_state.analiz_aktif = True

# --- FONKSİYONLAR ---
@st.cache_resource
def model_yukle():
    return pipeline("sentiment-analysis", model="ProsusAI/finbert")

def sirket_bilgisi_getir(sembol):
    try:
        hisse = yf.Ticker(sembol)
        info = hisse.info
        return {
            "İsim": info.get("longName", sembol),
            "Sektör": info.get("sector", "Bilinmiyor"),
            "Fiyat": info.get("currentPrice", 0),
            "Piyasa Değeri": info.get("marketCap", 0),
            "Özet": info.get("longBusinessSummary", "Bilgi yok.")
        }
    except: return None

def buyuk_sayi_formatla(sayi):
    if sayi >= 1e9: return f"{sayi / 1e9:.2f} Mlr $"
    elif sayi >= 1e6: return f"{sayi / 1e6:.2f} Mn $"
    else: return f"{sayi}"

def verileri_hazirla(sembol, periyot, aralik):
    try:
        hisse = yf.Ticker(sembol)
        df = hisse.history(period=periyot, interval=aralik)
        if df.empty: return None
        
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        return df
    except: return None

def grafik_ciz_rsi_ile(sembol, df, sma_goster=False):
    try:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.1, 
                            subplot_titles=(f'{sembol} Fiyat Hareketi', 'RSI (Momentum)'),
                            row_heights=[0.7, 0.3])

        renk = '#FF6D00' if secilen_aralik in ['15m', '60m'] else '#2962FF'
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name="Fiyat", line=dict(color=renk, width=2)), row=1, col=1)
        
        if sma_goster:
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], name="SMA 50", line=dict(color='#FFD600', width=2, dash='dash')), row=1, col=1)

        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color='#AA00FF', width=2)), row=2, col=1)
        fig.add_hline(y=70, line_dash="dot", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dot", line_color="green", row=2, col=1)

        # --- BURASI DÜZELTİLDİ: dragmode='pan' ---
        fig.update_layout(
            height=500, 
            xaxis_title="", 
            showlegend=False, 
            hovermode="x unified",
            dragmode='pan'  # <--- ARTIK SÜRÜKLEYİNCE KAYACAK, ZOOM YAPMAYACAK
        )
        return fig
    except: return None

def sinyal_uret(fiyat_df, duygu_df):
    karar = "BEKLE ⚪"
    trend = "NÖTR"
    
    son_fiyat = fiyat_df['Close'].iloc[-1]
    son_sma = fiyat_df['SMA_50'].iloc[-1]
    son_rsi = fiyat_df['RSI'].iloc[-1]
    
    if pd.isna(son_sma): trend = "Veri Yetersiz"
    elif son_fiyat > son_sma: trend = "YÜKSELİŞ 📈"
    else: trend = "DÜŞÜŞ 📉"

    rsi_durumu = "Normal"
    if son_rsi > 70: rsi_durumu = "AŞIRI PAHALI ⚠️"
    elif son_rsi < 30: rsi_durumu = "AŞIRI UCUZ ♻️"

    baskin_duygu = "Nötr"
    if not duygu_df.empty:
        baskin_duygu = duygu_df['Duygu'].mode()[0] 
    
    if trend == "YÜKSELİŞ 📈" and baskin_duygu == "positive": karar = "GÜÇLÜ AL 🟢"
    elif trend == "DÜŞÜŞ 📉" and baskin_duygu == "negative": karar = "GÜÇLÜ SAT 🔴"
    elif trend == "YÜKSELİŞ 📈" and baskin_duygu == "negative": karar = "DİKKATLİ OL ⚠️"
    elif trend == "DÜŞÜŞ 📉" and baskin_duygu == "positive": karar = "DİKKATLİ OL ⚠️"
        
    return karar, trend, baskin_duygu.upper(), rsi_durumu

def hisse_analiz_et(sembol, analizci):
    veriler = []
    try:
        hisse = yf.Ticker(sembol)
        haberler = hisse.news
        if haberler:
            for haber in haberler:
                icerik = haber.get('content', {})
                baslik = icerik.get('title', 'Başlık Yok')
                if baslik != 'Başlık Yok':
                    sonuc = analizci(baslik)[0]
                    veriler.append({"Tarih": pd.Timestamp.now(), "Hisse": sembol, "İçerik": baslik, "Duygu": sonuc['label'], "Skor": sonuc['score']})
    except: pass
    
    if not veriler:
        veriler.append({"Tarih": pd.Timestamp.now(), "Hisse": sembol, "İçerik": "Normal veri akışı.", "Duygu": "neutral", "Skor": 0.5})

    return pd.DataFrame(veriler)

# --- ANA PROGRAM ---
if st.session_state.analiz_aktif:
    sembol_listesi = [s.strip().upper() for s in hisse_girdisi.split(',') if s.strip() != ""]
    
    if not sembol_listesi:
        st.warning("Lütfen bir hisse kodu girin.")
    else:
        try:
            with st.spinner('Yapay Zeka Çalışıyor...'):
                analizci = model_yukle()
        except Exception as e:
            st.error(f"AI Hatası: {e}")
            st.stop()

        cols = st.columns(len(sembol_listesi))
        tum_raporlar = []

        for i, sembol in enumerate(sembol_listesi):
            with cols[i]:
                st.markdown(f"## {sembol}")
                
                df_fiyat = verileri_hazirla(sembol, secilen_periyot, secilen_aralik)
                df_duygu = hisse_analiz_et(sembol, analizci)
                tum_raporlar.append(df_duygu)

                if df_fiyat is not None:
                    karar, trend_durumu, duygu_durumu, rsi_mesaji = sinyal_uret(df_fiyat, df_duygu)
                    
                    st.info(f"🤖 **KARAR:** {karar}")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Trend", trend_durumu)
                    c2.metric("Piyasa", duygu_durumu)
                    c3.metric("RSI", f"{df_fiyat['RSI'].iloc[-1]:.1f}", delta=rsi_mesaji, delta_color="off")
                    st.divider()

                    fig = grafik_ciz_rsi_ile(sembol, df_fiyat, sma_aktif)
                    if fig: 
                        # scrollZoom=True ekledik ki tekerlekle zoom yapılabilsin
                        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
                else:
                    st.warning("Fiyat verisi alınamadı.")

                bilgi = sirket_bilgisi_getir(sembol)
                if bilgi:
                    with st.expander("🏢 Şirket Kimlik Kartı"):
                        st.write(f"**Sektör:** {bilgi['Sektör']}")
                        st.write(f"**Özet:** {bilgi['Özet']}")

        st.divider()
        if tum_raporlar:
            final_df = pd.concat(tum_raporlar)
            st.download_button("📥 Tam Analiz Raporunu İndir (CSV)", final_df.to_csv(index=False).encode('utf-8'), 'analiz.csv', 'text/csv')

# --- AÇILIŞ EKRANI ---
if not st.session_state.analiz_aktif:
    c1, c2, c3 = st.columns(3)
    c1.metric("Sistem Durumu", "Hazır", "Bekliyor", delta_color="off")
    c2.metric("Yapay Zeka", "FinBERT", "Aktif")
    c3.metric("Veri Kaynağı", "Canlı", "Yahoo Finance")
    st.image("https://images.unsplash.com/photo-1611974765270-ca12586343bb?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80", caption="Borsa Analiz Terminali")