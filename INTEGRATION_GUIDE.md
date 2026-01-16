# SMSPark Chatbot Entegrasyon Rehberi

Bu rehber, SMSPark Chatbot'unu mevcut web sitenize nasıl entegre edeceğinizi açıklar.

## 🚀 Hızlı Başlangıç

### 1. Flask Backend'i Çalıştırın

```bash
python web_interface.py
```

Backend `http://localhost:5000` adresinde çalışacaktır.

### 2. Chatbot Widget'ını Sitenize Ekleyin

#### Yöntem 1: HTML Include (Önerilen)

Sitenizin tüm sayfalarında görünen bir header veya footer dosyanız varsa, `chatbot_widget.html` dosyasını include edin:

```html
<!-- Header veya Footer dosyanızda -->
<?php include 'chatbot_widget.html'; ?>
<!-- veya -->
{% include 'chatbot_widget.html' %}
```

#### Yöntem 2: JavaScript ile Dinamik Yükleme

Sitenizin tüm sayfalarına bu kodu ekleyin (genellikle `</body>` etiketinden önce):

```html
<script>
// Chatbot Widget'ı dinamik olarak yükle
(function() {
    const script = document.createElement('script');
    script.src = 'http://localhost:5000/static/chatbot-widget.js';
    script.onload = function() {
        loadChatbotWidget('http://localhost:5000');
    };
    document.body.appendChild(script);
})();
</script>
```

#### Yöntem 3: Doğrudan HTML Ekleme

Sitenizin tüm sayfalarının `</body>` etiketinden önce `chatbot_widget.html` dosyasının içeriğini kopyalayın.

### 3. API Endpoint'i Güncelleyin

Eğer backend farklı bir domain'de çalışıyorsa, `chatbot_widget.html` dosyasındaki API URL'ini güncelleyin:

```javascript
const API_URL = 'https://your-domain.com/api/chat'; // Kendi domain'iniz
```

## 📋 Özellikler

✅ **Sağ altta floating button** - Tüm sayfalarda görünür  
✅ **Tıklandığında açılır** - Aynı sayfada popup olarak  
✅ **Kapatma butonu** - X butonu ile kapatılabilir  
✅ **WhatsApp desteği** - Sağ altta WhatsApp butonu  
✅ **Responsive tasarım** - Mobil uyumlu  
✅ **Yeni mesaj bildirimi** - Widget kapalıyken badge gösterir  

## 🎨 Özelleştirme

### Renkleri Değiştirme

`chatbot_widget.html` dosyasındaki CSS'i düzenleyin:

```css
/* Ana renkler */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
/* Kendi marka renklerinize göre değiştirin */
```

### Konumlandırma

Floating button'un konumunu değiştirmek için:

```css
#chatbot-toggle-btn {
    bottom: 20px;  /* Alt boşluk */
    right: 20px;   /* Sağ boşluk */
}
```

### Boyutlandırma

Widget boyutunu değiştirmek için:

```css
#chatbot-widget-container {
    width: 380px;   /* Genişlik */
    height: 600px;  /* Yükseklik */
}
```

## 🔧 Gelişmiş Kullanım

### CORS Ayarları (Farklı Domain'ler İçin)

Eğer widget farklı bir domain'den yükleniyorsa, `web_interface.py` dosyasına CORS desteği ekleyin:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Tüm origin'lere izin ver
# veya
CORS(app, resources={r"/api/*": {"origins": "https://your-domain.com"}})
```

### Özel Event'ler

Widget ile etkileşim için event listener'lar ekleyebilirsiniz:

```javascript
// Widget açıldığında
document.addEventListener('chatbotOpened', function() {
    console.log('Chatbot açıldı');
});

// Widget kapandığında
document.addEventListener('chatbotClosed', function() {
    console.log('Chatbot kapandı');
});
```

## 📱 Mobil Uyumluluk

Widget otomatik olarak mobil cihazlara uyum sağlar:
- Ekran genişliği 480px'den küçükse tam ekran moduna geçer
- Touch-friendly butonlar ve input alanları

## 🐛 Sorun Giderme

### Widget Görünmüyor

1. Browser console'u kontrol edin (F12)
2. JavaScript hatalarını kontrol edin
3. API endpoint'inin çalıştığından emin olun

### Mesajlar Gönderilmiyor

1. Network tab'ında API isteklerini kontrol edin
2. Backend loglarını kontrol edin
3. CORS ayarlarını kontrol edin

### Stil Sorunları

1. CSS çakışmalarını kontrol edin
2. `!important` kullanarak öncelik verin
3. Z-index değerlerini kontrol edin

## 📞 Destek

Sorularınız için:
- WhatsApp: 0543 726 59 86
- Email: destek@smspark.net

