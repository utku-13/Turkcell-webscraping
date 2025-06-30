# Turkcell Google Maps Review Scraper

Bu script Google Maps'te "turkcell" araması yaparak çıkan ilk 3 lokasyonun yorumlarını çeker.

## Kurulum

1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

2. Chrome browser'ınızın yüklü olduğundan emin olun

3. ChromeDriver'ın otomatik olarak yükleneceğinden emin olmak için Selenium 4.x kullanıyoruz

## Kullanım

Script'i çalıştırmak için:

```bash
python main.py
```

## Ne Yapar?

- Google Maps'te "turkcell" araması yapar
- İlk 3 lokasyonu bulur
- Her lokasyon için en yeni 10 yorumu çeker
- Her yorum için şu bilgileri gösterir:
  - Yorumcunun adı
  - Verdiği puan
  - Yorum metni

## Özellikler

- Otomatik bekleme süreleri (Google'ın anti-bot önlemlerine karşı)
- Rastgele gecikmeler
- Hata yakalama ve güvenli kapanma
- Temiz ve okunabilir çıktı formatı 