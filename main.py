import yfinance as yf
import pandas as pd  # Excel için gerekli kütüphane
from transformers import pipeline
import time

# --- AYARLAR ---
HISSE_KODU = "AAPL"
DOSYA_ADI = "Apple_Analiz_Raporu.xlsx"

print(f"--- {HISSE_KODU} İÇİN ANALİZ SİSTEMİ BAŞLATILIYOR ---\n")

# 1. YAPAY ZEKA YÜKLENİYOR
print("1. Adım: Yapay Zeka (FinBERT) hazırlanıyor...")
analizci = pipeline("sentiment-analysis", model="ProsusAI/finbert")
print("   >>> Yapay Zeka Hazır.\n")

# Analiz sonuçlarını burada toplayacağız
toplanan_veriler = []

# ---------------------------------------------------------
# 2. GERÇEK HABERLERİ ÇEKME (Modül A)
# ---------------------------------------------------------
print("2. Adım: Güncel Haberler Çekiliyor...")
try:
    hisse = yf.Ticker(HISSE_KODU)
    haberler = hisse.news
    
    if haberler:
        print(f"   >>> {len(haberler)} adet haber bulundu.")
        for haber in haberler:
            icerik = haber.get('content', {})
            baslik = icerik.get('title', 'Başlık Yok')
            link = icerik.get('clickThroughUrl', icerik.get('canonicalUrl', 'Link Yok'))
            
            if baslik != 'Başlık Yok':
                # Analiz Et
                sonuc = analizci(baslik)[0]
                
                # Listeye Ekle
                toplanan_veriler.append({
                    "Kaynak": "Haber (Yahoo)",
                    "Metin": baslik,
                    "Duygu": sonuc['label'],     # positive/negative
                    "Güven Skoru": f"%{sonuc['score']:.2f}",
                    "Link": link
                })
    else:
        print("   >>> Haber bulunamadı.")

except Exception as e:
    print(f"   >>> Hata: {e}")

# ---------------------------------------------------------
# 3. REDDIT SİMÜLASYONU (Modül B - Mock Data)
# ---------------------------------------------------------
print("\n3. Adım: Reddit Topluluk Yorumları Taranıyor (Simülasyon)...")
sahte_reddit_yorumlari = [
    "I am selling all my Apple stocks, vision pro is bad.",
    "Apple earnings will be huge next month, buying more!",
    "Tim Cook is a good CEO but market is slow.",
    "Tech sector is crashing, stay away from AAPL."
]

for yorum in sahte_reddit_yorumlari:
    # Analiz Et
    sonuc = analizci(yorum)[0]
    
    # Listeye Ekle
    toplanan_veriler.append({
        "Kaynak": "Reddit (Topluluk)",
        "Metin": yorum,
        "Duygu": sonuc['label'],
        "Güven Skoru": f"%{sonuc['score']:.2f}",
        "Link": "N/A"
    })

print(f"   >>> {len(sahte_reddit_yorumlari)} adet yorum analiz edildi.\n")

# ---------------------------------------------------------
# 4. EXCEL RAPORU OLUŞTURMA
# ---------------------------------------------------------
print("4. Adım: Excel Raporu Hazırlanıyor...")

if toplanan_veriler:
    # Veriyi Excel formatına (DataFrame) çevir
    df = pd.DataFrame(toplanan_veriler)
    
    # Dosyaya kaydet
    df.to_excel(DOSYA_ADI, index=False)
    
    print(f"\n✅ BAŞARILI! Rapor oluşturuldu: {DOSYA_ADI}")
    print("Klasörünü kontrol et, Excel dosyasını göreceksin.")
else:
    print("\n❌ Kaydedilecek veri bulunamadı.")