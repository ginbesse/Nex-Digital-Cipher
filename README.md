# Smart Device Code Generator

Bu proje, kullanıcı seçimine göre farklı cihaz ve dijital uygulama türlerine uygun, üretilebilir ve çalıştırılabilir çıktı paketleri üreten API-aware bir kod üreticisidir.

## Özellikler

- Website seçimi için domain ve URL bazlı üretim
- DNS over HTTPS (Google Public DNS) üzerinden alan adı metaverisi çekme
- ipify API üzerinden yayın IP bilgisi çekme
- Airplane, Car, Ship, Phone, Computer ve Digital App için şablon üretimi
- Termux kurulumu için yardımcı betik
- `generated/` altında örnek çıktı üretimi

## Desteklenen türler

- Website
- Airplane
- Car
- Ship
- Phone
- Computer
- Digital App

## Hızlı Başlangıç

### Python ile çalıştırma

```bash
python3 smart_device_generator.py
```

### Demo üretimi

```bash
python3 smart_device_generator.py --demo
```

### Termux kurulumu

```bash
sh termux_setup.sh
```

## Proje Yapısı

- `smart_device_generator.py` : Ana üretici betiği
- `termux_setup.sh` : Termux için kurulum betiği
- `scripts/run_demo.py` : Demo çalıştırma yardımcı betiği
- `docs/USAGE.md` : kullanım kılavuzu
- `generated/` : üretilen çıktılar

## Üretilen çıktı örneği

Website üretimi şu dosyaları oluşturur:

- `index.html`
- `styles.css`
- `script.js`
- `site_manifest.json`

## Notlar

Bu proje, gerçek donanım üretimi veya fiziksel bir chip için firmware derleme sağlar nitelikte değildir. Ama kullanıcı seçimi, kullanıcı sayısı, domain/URL ve canlı API verilerine göre işlenebilir ve üretilebilir proje iskeleti üretir.

## Lisans

MIT
