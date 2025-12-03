from transformers import pipeline

# 1. FinBERT Modelini Yüklüyoruz (İlk çalışmada indirme yapar)
print("Yapay Zeka modeli yükleniyor... (Bu işlem ilk seferde 1-2 dakika sürebilir)")

# "ProsusAI/finbert" finans dünyasının en popüler modelidir.
analizci = pipeline("sentiment-analysis", model="ProsusAI/finbert")

# 2. Test Cümleleri
ornekler = [
    "Apple profits are up by 20%",          # Olumlu
    "Tesla creates a new robot",            # Nötr
    "Company creates huge debt crisis"      # Olumsuz
]

print("\n--- Analiz Başlıyor ---\n")

# 3. Analiz Yap
for cumle in ornekler:
    sonuc = analizci(cumle)[0]
    etiket = sonuc['label']
    skor = sonuc['score']
    
    print(f"Cümle: {cumle}")
    print(f"Karar: {etiket} (Güven: %{skor:.2f})")
    print("-" * 30)