import schedule
import time
import yfinance as yf
import pandas as pd
from transformers import pipeline
from datetime import datetime

print("🤖 Borsa Robotu Başlatıldı... (Çıkmak için Ctrl+C yapabilirsin)")

# 1. Yapay Zekayı Bir Kez Yükle (Bellekte kalsın)
print("   >>> Yapay Zeka yükleniyor, lütfen bekleyin...")
analizci = pipeline("sentiment-analysis", model="ProsusAI/finbert")
print("   >>> Hazır! Görev bekleniyor.\n")

def gorev():
    zaman_damgasi = datetime.now().strftime("%H:%M:%S")
    print(f"[{zaman_damgasi}] 🔄 Tarama Başladı...")
    
    veriler = []
    
    # --- Haberleri Çek ---
    try:
        hisse = yf.Ticker("AAPL")
        haberler = hisse.news
        if haberler:
            for haber in haberler:
                icerik = haber.get('content', {})
                baslik = icerik.get('title', 'Başlık Yok')
                if baslik != 'Başlık Yok':
                    sonuc = analizci(baslik)[0]
                    veriler.append({
                        "Zaman": zaman_damgasi,
                        "Tip": "Haber",
                        "Metin": baslik,
                        "Duygu": sonuc['label']
                    })
    except Exception as e:
        print(f"Hata: {e}")

    # --- Sonuçları Kaydet (Append Modu) ---
    if veriler:
        df = pd.DataFrame(veriler)
        # Var olan Excel'in üzerine ekleme yapmak zordur, şimdilik CSV (Metin) dosyasına ekleyelim
        # mode='a' (append) dosyayı silmeden altına ekler.
        df.to_csv("robot_raporu.csv", mode='a', header=False, index=False)
        print(f"   ✅ {len(veriler)} yeni veri 'robot_raporu.csv' dosyasına eklendi.")
    else:
        print("   ❌ Yeni veri bulunamadı.")

# --- ZAMANLAMA AYARLARI ---
# Test için her 30 saniyede bir çalıştırıyoruz.
# Gerçek hayatta: schedule.every().day.at("08:00").do(gorev)
schedule.every(30).seconds.do(gorev)

# --- SONSUZ DÖNGÜ ---
gorev() # İlk açılışta bir kere hemen çalışsın
while True:
    schedule.run_pending()
    time.sleep(1)