# SMSPark Destek Chatbotu

Ticket geçmişinden öğrenen, akıllı müşteri destek chatbot sistemi.

## 🎯 Özellikler

- **Akıllı Sorun Tanıma**: Kullanıcı mesajlarından otomatik olarak sorun tipini belirler
- **Bağlama Uygun Cevaplar**: Ticket geçmişinden öğrenen, doğru çözümler sunan yapı
- **Doğal Dil İşleme**: Türkçe dil desteği ile insan gibi konuşur
- **Adım Adım Çözümler**: Teknik sorunlarda detaylı çözüm adımları sunar
- **Ek Bilgi Talep Etme**: Gerektiğinde kullanıcıdan ek bilgi ister
- **Kısa ve Net**: Gereksiz uzunluklardan kaçınır, çözüm odaklıdır

## 📊 Analiz Edilen Veriler

- **1920+ destek ticket** analiz edildi
- **19 cevap şablonu** tespit edildi
- **En sık karşılaşılan sorunlar**:
  - Bakiye sorunları (590 ticket)
  - Numara sorunları (386 ticket)
  - SMS gelmeme (200 ticket)
  - Hesap sorunları (137 ticket)

## 🚀 Kurulum

### Gereksinimler

```bash
pip install flask
```

### Kullanım

#### 1. Komut Satırı Arayüzü

```bash
python chatbot.py
```

#### 2. Web Arayüzü

```bash
python web_interface.py
```

Tarayıcınızda http://localhost:5000 adresini açın.

## 📁 Dosya Yapısı

```
smspark-ai/
├── tickets.sql              # Ticket verileri (SQL)
├── ticket_messages.sql      # Ticket mesajları (SQL)
├── cevaplar.txt             # Cevap şablonları
├── analyze_data.py          # Veri analiz scripti
├── chatbot.py               # Ana chatbot modülü
├── web_interface.py         # Flask web arayüzü
├── templates/
│   └── index.html          # Web arayüzü HTML
└── README.md               # Bu dosya
```

## 🔧 Chatbot Özellikleri

### Sorun Kategorileri

Chatbot şu sorun kategorilerini tanır:

1. **SMS Gelmiyor**: SMS/onay kodu alma sorunları
2. **Hesap Kapandı**: Hesap kapatılma/engelleme sorunları
3. **Bakiye**: Ödeme ve bakiye sorunları
4. **Numara**: Numara satın alma/iptal sorunları
5. **Stok**: Stok bulunamama sorunları
6. **WhatsApp/Telegram**: Platforma özel sorunlar

### Örnek Kullanım

```
Kullanıcı: SMS gelmiyor
Chatbot: SMS alamıyor iseniz bunun birkaç nedeni olabilir. Öncelikle, 
         eğer sitemizden hizmet almadan önce ücretsiz veya ücretli 
         servislerde numara aktifleştirme denemesi yaptıysanız cihazınız 
         mimlenmiş olabilir ve cihazınızı en az 24 saat dinlendirmeniz 
         gerekmektedir. 1) Telegram ve Whatsapp'a sadece telefon kullanarak 
         telefon uygulamalarından kayıt olabilirsiniz...
```

### API Kullanımı

```python
from chatbot import SupportChatbot

chatbot = SupportChatbot()
response = chatbot.generate_response("SMS gelmiyor")
print(response)
```

## 🎓 Analiz Süreci

1. **Veri Analizi**: SQL dosyalarından ticket ve mesaj verileri çıkarıldı
2. **Kategorilendirme**: Sorunlar kategorilere ayrıldı
3. **Şablon Oluşturma**: Cevap şablonları kategorilere göre gruplandı
4. **Pattern Matching**: Anahtar kelime eşleştirme sistemi kuruldu
5. **Çözüm Adımları**: Her kategori için adım adım çözümler belirlendi

## 🔍 Sorun Tespit Algoritması

Chatbot, kullanıcı mesajını analiz ederek:

1. Anahtar kelimeleri tespit eder
2. Sorun tipini belirler (confidence score ile)
3. En uygun şablonu seçer
4. Gerekirse ek bilgi ister
5. Özelleştirilmiş cevap üretir

## 📝 Geliştirme Notları

- Chatbot, gerçek ticket verilerinden öğrenir
- Her kategori için öncelik skoru belirlenmiştir
- Cevaplar kısa ve çözüm odaklı tutulmuştur
- Gereksiz uzun açıklamalardan kaçınılmıştır

## 🛠️ Gelecek Geliştirmeler

- [ ] Daha gelişmiş NLP (spaCy/NLTK)
- [ ] Machine learning modeli entegrasyonu
- [ ] Çoklu dil desteği
- [ ] Sentiment analizi
- [ ] Ticket sistemi entegrasyonu
- [ ] Kullanıcı geri bildirim sistemi

## 📄 Lisans

Bu proje SMSPark için geliştirilmiştir.

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Push edin (`git push origin feature/AmazingFeature`)
5. Pull Request açın

## 📧 İletişim

Sorularınız için destek sistemi üzerinden iletişime geçebilirsiniz.

---

**Not**: Bu chatbot, mevcut ticket verilerinden öğrenen bir sistemdir. Gerçek müşteri hizmetleri deneyimini simüle eder.

