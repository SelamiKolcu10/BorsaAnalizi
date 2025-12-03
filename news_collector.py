import yfinance as yf

print("--- Apple (AAPL) Haberleri Çekiliyor ---")

try:
    hisse = yf.Ticker("AAPL")
    haberler = hisse.news
    
    if haberler:
        print(f"\nToplam {len(haberler)} adet haber bulundu.\n")
        
        for i, haber in enumerate(haberler, 1):
            # ÖNCE 'content' KUTUSUNU AÇIYORUZ
            icerik = haber.get('content', {})
            
            # ŞİMDİ İÇİNDEN BİLGİLERİ ALIYORUZ
            baslik = icerik.get('title', 'Başlık Yok')
            ozet = icerik.get('summary', 'Özet Yok')
            
            # Link bazen 'canonicalUrl' bazen 'clickThroughUrl' olabilir
            link = icerik.get('canonicalUrl', icerik.get('clickThroughUrl', 'Link Yok'))
            
            print(f"{i}. {baslik}")
            print(f"   Link: {link}")
            print("-" * 50) # Araya çizgi çekelim
            
    else:
        print("Haber listesi boş geldi.")

except Exception as e:
    print(f"Hata oluştu: {e}")