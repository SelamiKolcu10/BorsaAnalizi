from transformers import pipeline
import time

# 1. Yapay Zekayı Hazırla
print("FinBERT Modeli Yükleniyor... (Biraz bekleyin)")
analizci = pipeline("sentiment-analysis", model="ProsusAI/finbert")

# 2. SAHTE REDDIT VERİSİ (Mock Data)
# Gerçek API çalışana kadar bu listeyi kullanacağız.
# Sanki r/stocks subredditinden çekilmiş Apple yorumları gibi:
sahte_reddit_yorumlari = [
    "Apple Vision Pro is a total disaster, returning mine immediately.",  # Kötü yorum
    "Just bought more AAPL shares, earnings report looks solid!",         # İyi yorum
    "Tim Cook sold some shares but I think it is standard procedure.",    # Nötr/Belirsiz
    "Apple's new AI features are going to change everything, bullish!",   # Çok iyi yorum
    "Market is crashing, selling all my tech stocks including Apple."     # Kötü yorum
]

print(f"\n--- SİMÜLASYON MODU: {len(sahte_reddit_yorumlari)} Yorum Analiz Ediliyor ---\n")
time.sleep(1) # Gerçekçilik için azıcık bekleme

# 3. Analiz Döngüsü
toplam_skor = 0

for i, yorum in enumerate(sahte_reddit_yorumlari, 1):
    # Yapay Zeka Okuyor...
    sonuc = analizci(yorum)[0]
    
    etiket = sonuc['label']  # positive, negative, neutral
    guven = sonuc['score']
    
    # Ekrana Bas
    print(f"[{i}] Yorum: {yorum}")
    print(f"    >>> ANALİZ: {etiket.upper()} (Güven: %{guven:.2f})")
    print("-" * 50)

print("\nSimülasyon Başarıyla Tamamlandı.")