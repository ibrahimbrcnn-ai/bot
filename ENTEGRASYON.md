# SMSPark Chatbot Entegrasyon Rehberi (Türkçe)

## 🎯 Özellikler

✅ Sağ altta floating button (baloncuk) - Tüm sayfalarda görünür  
✅ Tıklandığında açılır - Aynı sayfada popup olarak  
✅ Kapatma butonu (X) - Widget'ı kapatır  
✅ WhatsApp desteği - Sağ altta WhatsApp butonu  
✅ Responsive tasarım - Mobil uyumlu  
✅ Yeni mesaj bildirimi - Widget kapalıyken badge gösterir  

## 📦 Kurulum

### 1. Backend'i Çalıştırın

```bash
cd C:\Users\İbrahim Bircan\Desktop\smspark-ai
python web_interface.py
```

Backend `http://localhost:5000` adresinde çalışacaktır.

### 2. Widget'ı Sitenize Ekleyin

#### Yöntem 1: Doğrudan HTML Ekleme (En Kolay)

Sitenizin **tüm sayfalarının** `</body>` etiketinden **ÖNCE** `templates/chatbot_widget.html` dosyasının içeriğini kopyalayın.

**Örnek:**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Benim Sitem</title>
</head>
<body>
    <!-- Sitenizin içeriği -->
    
    <!-- Chatbot Widget - BURAYA EKLEYİN -->
    <!-- templates/chatbot_widget.html dosyasının içeriğini buraya yapıştırın -->
    
</body>
</html>
```

#### Yöntem 2: PHP Include (Eğer PHP kullanıyorsanız)

Eğer sitenizde header/footer dosyaları varsa:

```php
<!-- footer.php veya header.php dosyanızda -->
<?php include 'templates/chatbot_widget.html'; ?>
```

#### Yöntem 3: JavaScript ile Dinamik Yükleme

Sitenizin tüm sayfalarına bu kodu ekleyin (`</body>` etiketinden önce):

```html
<script>
(function() {
    fetch('http://localhost:5000/widget')
        .then(response => response.text())
        .then(html => {
            const div = document.createElement('div');
            div.innerHTML = html;
            document.body.appendChild(div);
        });
})();
</script>
```

### 3. API URL'ini Güncelleyin

Eğer backend farklı bir domain'de çalışıyorsa, `chatbot_widget.html` dosyasındaki şu satırı güncelleyin:

```javascript
const API_URL = '/api/chat'; // Kendi domain'iniz için: 'https://your-domain.com/api/chat'
```

## 🎨 Özelleştirme

### Renkleri Değiştirme

`chatbot_widget.html` dosyasındaki CSS'i düzenleyin:

```css
/* Ana renkler - Kendi marka renklerinize göre değiştirin */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Konumlandırma

Floating button'un konumunu değiştirmek için:

```css
#chatbot-toggle-btn {
    bottom: 20px;  /* Alt boşluk */
    right: 20px;   /* Sağ boşluk */
    /* Sol taraf için: right: auto; left: 20px; */
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

## 🔧 Gelişmiş Ayarlar

### Farklı Domain'ler İçin CORS

Eğer widget farklı bir domain'den yükleniyorsa, `web_interface.py` dosyasına CORS desteği ekleyin:

```bash
pip install flask-cors
```

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Tüm origin'lere izin ver
```

### Production için

Production ortamında:

1. **HTTPS kullanın** - Güvenlik için
2. **API URL'ini güncelleyin** - Production domain'inize göre
3. **CORS ayarlarını sınırlayın** - Sadece kendi domain'inize izin verin

```python
CORS(app, resources={r"/api/*": {"origins": "https://your-domain.com"}})
```

## 📱 Mobil Uyumluluk

Widget otomatik olarak mobil cihazlara uyum sağlar:
- Ekran genişliği 480px'den küçükse tam ekran moduna geçer
- Touch-friendly butonlar ve input alanları

## 🐛 Sorun Giderme

### Widget Görünmüyor

1. Browser console'u açın (F12)
2. JavaScript hatalarını kontrol edin
3. Backend'in çalıştığından emin olun: `http://localhost:5000/api/health`

### Mesajlar Gönderilmiyor

1. Network tab'ında API isteklerini kontrol edin (F12 > Network)
2. Backend loglarını kontrol edin
3. CORS ayarlarını kontrol edin

### Stil Sorunları

1. CSS çakışmalarını kontrol edin
2. `!important` kullanarak öncelik verin
3. Z-index değerlerini kontrol edin (widget: 9999, button: 9998)

## 📞 Test

1. Backend'i çalıştırın: `python web_interface.py`
2. Widget'ı bir test sayfasına ekleyin
3. Sağ alttaki baloncuk butonuna tıklayın
4. Mesaj gönderip test edin

## 🎉 Tamamlandı!

Artık chatbot'unuz tüm sayfalarda sağ altta baloncuk olarak görünecek ve tıklandığında açılacak!

