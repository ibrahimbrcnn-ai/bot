#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Akıllı Destek Chatbotu
Ticket geçmişinden öğrenen, doğal dil işleme kullanan destek asistanı
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict

class SupportChatbot:
    """Ticket verilerinden öğrenen akıllı destek chatbotu"""
    
    def __init__(self):
        """Chatbot'u başlatır ve verileri yükler"""
        self.templates = self._load_templates()
        self.keywords = self._extract_keywords()
        self.problem_patterns = self._load_problem_patterns()
        self.context_history = []
        
    def _load_templates(self) -> Dict[str, List[str]]:
        """Cevap şablonlarını yükler"""
        with open('cevaplar.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Boş satırlarla ayrılmış şablonlar
        templates_raw = [t.strip() for t in content.split('\n\n') if t.strip()]
        
        # Şablonları kategorilere göre grupla
        templates = {
            'sms_gelmiyor': [],
            'hesap_kapandı': [],
            'bakiye': [],
            'numara': [],
            'stok': [],
            'hata': [],
            'numara_kalıcılık': [],
            'ödeme_bildirimi': [],
            'genel': []
        }
        
        for template in templates_raw:
            template_lower = template.lower()
            categorized = False
            
            # SMS gelmiyor şablonları (en önce kontrol et)
            if ('sms' in template_lower and ('gelmiyor' in template_lower or 'gelmedi' in template_lower)) or \
               ('sms alamıyor' in template_lower) or ('telegram ve whatsapp\'a sadece telefon' in template_lower):
                templates['sms_gelmiyor'].append(template)
                categorized = True
            # Hesap kapandı
            elif 'hesap' in template_lower and ('kapandı' in template_lower or 'kapatılan' in template_lower or 'kapatılabilir' in template_lower):
                templates['hesap_kapandı'].append(template)
                categorized = True
            # Bakiye
            elif 'bakiye' in template_lower or ('para' in template_lower and ('iade' in template_lower or 'yüklenmedi' in template_lower)):
                templates['bakiye'].append(template)
                categorized = True
            # Numara kalıcılık
            elif 'numara' in template_lower and ('kalıcı' in template_lower or '2fa' in template_lower or 'iki faktörlü' in template_lower):
                templates['numara_kalıcılık'].append(template)
                categorized = True
            # Numara tek kullanım
            elif 'numara' in template_lower and 'tek kullanım' in template_lower:
                templates['numara'].append(template)
                categorized = True
            # Stok
            elif 'stok' in template_lower:
                templates['stok'].append(template)
                categorized = True
            # Hata
            elif 'hata' in template_lower or 'geçici yasak' in template_lower:
                templates['hata'].append(template)
                categorized = True
            # Ödeme bildirimi
            elif 'ödeme bildirim' in template_lower or 'ödeme yaptığınız' in template_lower or ('ödeme' in template_lower and 'bildirim' in template_lower):
                templates['ödeme_bildirimi'].append(template)
                categorized = True
            
            # Eğer hiçbir kategoriye uymadıysa genel'e ekle
            if not categorized:
                templates['genel'].append(template)
        
        return templates
    
    def _extract_keywords(self) -> Dict[str, List[str]]:
        """Anahtar kelimeleri çıkarır - ticket verilerinden öğrenilen kelimeler"""
        return {
            'sms_gelmiyor': [
                'sms gelmiyor', 'sms gelmedi', 'kod gelmiyor', 'kod gelmedi',
                'onay kodu gelmiyor', 'onay kodu gelmedi', 'sms kodu gelmiyor',
                'doğrulama kodu gelmiyor', 'sms alamıyorum', 'kod alamıyorum',
                'numara aldım ama kod gelmiyor', 'hiçbir numarada kod gelmiyor',
                'doğrulama yapamıyorum', 'sms bekleniyor', 'sms gönderilmiyor'
            ],
            'hesap_kapandı': [
                'hesap kapandı', 'hesabım kapandı', 'hesap kapatıldı', 'hesap engellendi',
                'hesap kısıtlandı', 'hesabım kısıtlandı', 'hesap kıtıstlandı',  # typo'lar dahil
                'whatsapp hesabım kapandı', 'whatsapp hesabım kısıtlandı',
                'telegram hesabım kapandı', 'telegram hesabım kısıtlandı',
                'aldığım numara kapandı', 'numara kapandı', 'numaram kapandı',
                'spam yedi', 'spamdan kapandı', 'spam nedeniyle kapandı',
                'hesaba girer girmez kapandı', 'güvenlik nedeniyle kapandı',
                'ban yedi numara', 'hesap spam', 'güvenlik uyarısı',
                'hesap kapanıyor', 'numaralar kapandı', 'numaralar kapanıyor',
                'güvenlik nedeniyle hesap', 'hesap engellendi', 'hesap yasaklandı'
            ],
            'bakiye': [
                'bakiye', 'bakiye gelmedi', 'para', 'para gelmedi', 'ödeme',
                'yatırma', 'yatırdım', 'havale', 'eft', 'para iadesi', 'iade',
                'bakiye yükleme', 'para yatırma', 'bakiye yüklemesi',
                'para yatırdım', 'ödeme yaptım', 'hesaba geçmedi',
                'param nerede', 'bakiyem nerede'
            ],
            'numara': [
                'numara', 'numara aldım', 'numara alamıyorum', 'numara istiyorum',
                'numara geçersiz', 'numara iptal', 'numara kullanılıyor',
                'numara satın almak', 'numara satın alma', 'numara kiralamak',
                'numara kiralama', 'numara ne zaman', 'numara kaç gün'
            ],
            'whatsapp': [
                'whatsapp', 'whatsap', 'wp', 'whatsapp numarası',
                'whatsapp hesabı', 'whatsapp 1', 'whatsapp 2'
            ],
            'telegram': [
                'telegram', 'tg', 'telegram numarası', 'telegram hesabı',
                'telegram 2', 'telegram 1'
            ],
            'stok': [
                'stok yok', 'stok sorunu', 'numara bulunmuyor', 'stok bulunmuyor'
            ],
            'numara_kalıcılık': [
                'numara kalıcı', 'numara süre', 'numara kaç gün',
                'numara ne kadar', 'numara kiralama'
            ],
            'ödeme_bildirimi': [
                'ödeme yaptım', 'para yatırdım', 'havale yaptım',
                'eft yaptım', 'ödeme bildirimi', 'bakiye yükleme'
            ]
        }
    
    def _load_problem_patterns(self) -> Dict[str, Dict]:
        """Sorun kalıplarını yükler"""
        return {
            'sms_gelmiyor': {
                'priority': 10,
                'solutions': [
                    'Cihazınızı 24 saat dinlendirin',
                    'Telefon uygulamasından kayıt olun (bilgisayar kullanmayın)',
                    'Kaliteli numara seçin',
                    'VPN kullanın',
                    'Numarayı iptal edip yeniden deneyin',
                    'WhatsApp 1 kategorisi veya Telegram için Amerika/Kanada/İngiltere kullanın'
                ],
                'requires_info': ['hangi uygulama', 'hangi ülke', 'bilgisayar mı telefon mu']
            },
            'hesap_kapandı': {
                'priority': 9,
                'solutions': [
                    'Hesap açtıktan 24 saat sonra ilk mesajınızı gönderin',
                    'WhatsApp Business kullanmayın',
                    'Spam davranışından kaçının',
                    'Numara sağlayıcı tarafından kapatıldıysa sorumluluk kabul edilmemektedir'
                ],
                'requires_info': ['ne zaman açıldı', 'hangi uygulama']
            },
            'bakiye': {
                'priority': 8,
                'solutions': [
                    'Ödeme bildirimi yaptınız mı?',
                    'Ödeme tarihi ve saati nedir?',
                    'SMS alana kadar ödeme alınmaz, ancak numara alımı başladığında hizmet kullanılmış sayılır',
                    'Kredi kartı/bankaya para iadesi mümkün değildir',
                    'Bakiye iadesi yapılabilir'
                ],
                'requires_info': ['ödeme tarihi', 'ödeme şekli', 'tutar']
            },
            'numara': {
                'priority': 7,
                'solutions': [
                    'Numara tek kullanımlıktır',
                    'Sınırsız SMS için numara kiralamalısınız',
                    '2FA (iki faktörlü doğrulama) ile kalıcı hale getirilebilir',
                    'Numara iptal edilince bakiye otomatik iade olur'
                ],
                'requires_info': ['hangi amaçla kullanacaksınız']
            },
            'stok': {
                'priority': 6,
                'solutions': [
                    'Diğer ülkeleri deneyin',
                    'WhatsApp 1 kategorisi veya Telegram için Amerika, Kanada, İngiltere kullanın',
                    'Kaliteli numaralar genelde stokludur',
                    'Ucuz numaralarda stok sorunu yaşanabilir'
                ],
                'requires_info': ['hangi servis', 'hangi ülke']
            }
        }
    
    def classify_problem(self, user_message: str) -> Tuple[str, float]:
        """Kullanıcı mesajından sorun tipini belirler - ticket verilerinden öğrenilen mantık"""
        user_message_lower = user_message.lower().strip()
        
        # Selamlama mesajları
        greetings = ['selam', 'selamlar', 'merhaba', 'iyi günler', 'merhabalar', 'sa', 'hey']
        if any(greeting in user_message_lower for greeting in greetings) and len(user_message_lower.split()) <= 2:
            return 'selamlama', 1.0
        
        # Önce spesifik ifadeleri kontrol et (uzun phrase'ler öncelikli)
        scores = defaultdict(float)
        
        # Anahtar kelime eşleşmeleri - uzun phrase'ler daha yüksek skor alır
        for problem_type, keywords in self.keywords.items():
            # Önce uzun kelimeleri kontrol et
            sorted_keywords = sorted(keywords, key=lambda x: len(x.split()), reverse=True)
            for keyword in sorted_keywords:
                if keyword in user_message_lower:
                    # Uzun phrase daha yüksek skor (2-3 kelimeli = 6-9 skor)
                    phrase_length = len(keyword.split())
                    score = phrase_length * 4  # Uzun phrase'ler daha önemli
                    scores[problem_type] += score
                    # Aynı mesajda başka eşleşme olmasın diye break etme - hepsini topla
        
        # Problem kalıplarına göre ekstra skor (priority)
        for problem_type, pattern_info in self.problem_patterns.items():
            if problem_type in scores:
                scores[problem_type] += pattern_info['priority'] * 3  # Priority daha etkili
        
        # Özel durumlar: "kapandı", "kısıtlandı", "engellendi" kelimeleri için context kontrolü
        closed_keywords = ['kapandı', 'kapatıldı', 'kapalı', 'kısıtlandı', 'kıtıstlandı', 
                          'engellendi', 'yasaklandı', 'ban', 'yasak']
        
        for closed_keyword in closed_keywords:
            if closed_keyword in user_message_lower:
                # "hesap", "whatsapp", "telegram" veya "numara" ile birlikte mi?
                if any(word in user_message_lower for word in ['hesap', 'hesabım', 'whatsapp', 'telegram', 'wp', 'tg']):
                    scores['hesap_kapandı'] += 20  # Çok yüksek skor
                elif any(word in user_message_lower for word in ['numara', 'numaram', 'aldığım']):
                    scores['hesap_kapandı'] += 15  # Numara kapandı da hesap_kapandı kategorisi
                else:
                    # Sadece "kapandı" kelimesi bile yeterli
                    scores['hesap_kapandı'] += 10
        
        # En yüksek skorlu problemi döndür
        if scores:
            best_problem = max(scores.items(), key=lambda x: x[1])
            # Confidence hesaplama iyileştirildi
            max_possible_score = 50.0  # Maksimum olası skor
            confidence = min(best_problem[1] / max_possible_score, 1.0)
            
            # Eğer confidence yeterince yüksekse o kategoriyi döndür
            # Threshold düşürüldü - daha hassas algılama
            if confidence > 0.15:  # Daha da düşürüldü
                return best_problem[0], confidence
        
        # Gerçekten anlaşılamadıysa
        return 'anlasilamadi', 0.0
    
    def find_template(self, problem_type: str, user_message: str = "") -> Optional[str]:
        """Problem tipine uygun şablon bulur"""
        # Önce spesifik kategoriyi kontrol et
        if problem_type in self.templates and self.templates[problem_type]:
            # İlk şablonu döndür
            return self.templates[problem_type][0]
        
        # Şablon bulunamadıysa None döndür (generate_response'da özel mesaj verilecek)
        return None
    
    def needs_more_info(self, problem_type: str, user_message: str) -> Tuple[bool, Optional[str]]:
        """Ek bilgi gerekip gerekmediğini kontrol eder"""
        if problem_type not in self.problem_patterns:
            return False, None
        
        pattern_info = self.problem_patterns[problem_type]
        user_message_lower = user_message.lower()
        
        # Gerekli bilgilerin var olup olmadığını kontrol et
        for info_key in pattern_info.get('requires_info', []):
            # Basit kontrol - gerçek uygulamada daha gelişmiş olmalı
            if info_key not in user_message_lower:
                return True, f"Daha iyi yardımcı olabilmem için {info_key} hakkında bilgi verir misiniz?"
        
        return False, None
    
    def generate_response(self, user_message: str, context: List[str] = None) -> str:
        """Kullanıcı mesajına cevap üretir"""
        if context:
            self.context_history.extend(context)
        
        self.context_history.append(user_message)
        
        # Problem tipini belirle
        problem_type, confidence = self.classify_problem(user_message)
        
        # Ek bilgi gerekiyor mu?
        needs_info, info_request = self.needs_more_info(problem_type, user_message)
        if needs_info and confidence < 0.7:
            return info_request
        
        # Selamlama mesajları için özel cevap
        if problem_type == 'selamlama':
            return "Merhaba! SMSPark destek ekibine hoş geldiniz. Size nasıl yardımcı olabilirim? Lütfen sorununuzu kısaca açıklayabilir misiniz?\n\nÖrnek sorunlar:\n- SMS/Kod gelmiyor\n- Bakiye/Ödeme sorunu\n- Numara alamıyorum\n- Hesap/Numara kapandı veya kısıtlandı\n- Stok yok"
        
        # Şablonu bul
        template = self.find_template(problem_type, user_message)
        
        if not template:
            # Şablon bulunamadıysa, problem tipine göre özel mesaj ver
            if problem_type == 'sms_gelmiyor':
                return "Merhaba. SMS gelmeme sorununuz için birkaç kontrol yapmanız gerekiyor:\n\n1) Cihazınızı 24 saat dinlendirin\n2) Telefon uygulamasından kayıt olun (bilgisayar kullanmayın)\n3) Kaliteli numara seçin\n4) Gerekirse VPN kullanın\n5) Numara iptal edip yeniden deneyin\n\nEğer sorun devam ederse canlı destek hattımıza ulaşabilirsiniz."
            elif problem_type == 'bakiye':
                return "Merhaba. Bakiye sorununuzla ilgili olarak, ödeme bildirimi yaptınız mı? Ödeme yaptıysanız tarih ve saati paylaşabilir misiniz? Elle kontrol edip bakiyenizi işleyebiliriz."
            elif problem_type == 'hesap_kapandı':
                return "Merhaba. Hesap/numara kapandı sorununuz için:\n\nYeni açılan hesaplar çeşitli nedenlerle kapatılabilir:\n\n1) Hesap açtıktan 24 saat sonra ilk mesajınızı gönderin\n2) WhatsApp Business kullanmayın\n3) Spam davranışından kaçının (çok fazla mesaj göndermeyin)\n4) Mimlenmiş cihaz/IP'den giriş yapmayın\n\nNumara aktif edildikten sonra kapatılan hesaplar için sorumluluk kabul edilmemektedir. Bu bilgiler kullanıcı sözleşmemizde belirtilmektedir.\n\nEğer sorun devam ederse, canlı destek hattımıza ulaşabilirsiniz."
            elif problem_type == 'numara':
                return "Merhaba. Numara sorununuzla ilgili: Satın aldığınız numara tek kullanımlıktır. Sınırsız SMS için numara kiralamanız gerekir. 2FA (iki faktörlü doğrulama) ile kalıcı hale getirebilirsiniz."
            elif problem_type == 'stok':
                return "Merhaba. Stok sorunu için: Diğer ülkeleri deneyin, WhatsApp 1 kategorisi veya Telegram için Amerika, Kanada, İngiltere kullanın. Kaliteli numaralar genelde stokludur."
            elif problem_type == 'anlasilamadi':
                return "Merhaba. Sorununuzu daha detaylı açıklayabilir misiniz? Size en iyi şekilde yardımcı olabilmem için hangi konuda destek almak istiyorsunuz?\n\nÖrnek sorunlar:\n- SMS/Kod gelmiyor\n- Bakiye/Ödeme sorunu\n- Numara alamıyorum\n- Hesap kapandı\n- Stok yok"
            else:
                # Diğer problem tipleri için genel mesaj
                return "Merhaba. Sorununuzu anladım. Daha detaylı bilgi verebilir misiniz? Size en iyi çözümü sunabilmem için biraz daha açıklama yapabilir misiniz?"
        
        # Cevabı özelleştir
        response = self._customize_response(template, problem_type, user_message)
        
        return response
    
    def _customize_response(self, template: str, problem_type: str, user_message: str) -> str:
        """Şablonu kullanıcı mesajına göre özelleştirir"""
        response = template
        
        # Kullanıcı mesajından çıkarılabilecek bilgiler
        user_lower = user_message.lower()
        
        # Kısa ve öz yap - gereksiz uzunlukları kısalt
        if len(response) > 800:
            # En önemli kısmı al
            if problem_type == 'sms_gelmiyor':
                # Adım adım çözümü vurgula
                if '1)' in response or '1.' in response:
                    # Numaralandırılmış liste varsa kullan
                    pass
                else:
                    # İlk 2-3 cümleyi al
                    sentences = response.split('.')
                    response = '. '.join(sentences[:3]) + '.'
        
        # Selamlama ekle (eğer yoksa)
        if not response.lower().startswith(('merhaba', 'iyi günler', 'merhaba.')):
            # Kısa ve samimi selamlama
            if len(response) > 200:
                response = "Merhaba. " + response
            else:
                response = "Merhaba. " + response
        
        # Kapanış ekle (eğer yoksa ve uzunsa)
        if len(response) > 300 and 'Başka bir arzunuz' not in response and 'yardımcı olabilirim' not in response.lower():
            response += " Başka bir konuda yardımcı olabilmem için lütfen bilgi verin."
        
        return response
    
    def get_solution_steps(self, problem_type: str) -> List[str]:
        """Problem tipine göre adım adım çözüm listesi döndürür"""
        if problem_type in self.problem_patterns:
            return self.problem_patterns[problem_type].get('solutions', [])
        return []
    
    def handle_followup(self, user_message: str) -> str:
        """Takip mesajlarını işler"""
        user_lower = user_message.lower()
        
        # Teşekkür, çözüldü vb.
        if any(word in user_lower for word in ['teşekkür', 'teşekkürler', 'sağol', 'çözüldü', 'tamam', 'oldu']):
            return "Rica ederim! Başka bir konuda yardımcı olabilmem için lütfen bilgi verin. İyi günler!"
        
        # Daha fazla bilgi isteği
        if any(word in user_lower for word in ['nasıl', 'neden', 'ne zaman', 'nerede']):
            # Son bağlamı kontrol et
            if self.context_history:
                last_problem, _ = self.classify_problem(self.context_history[-1])
                solutions = self.get_solution_steps(last_problem)
                if solutions:
                    response = "Adım adım çözüm:\n\n"
                    for i, solution in enumerate(solutions[:5], 1):  # Max 5 adım
                        response += f"{i}. {solution}\n"
                    return response
        
        # Yeni soru - normal akışa dön
        return self.generate_response(user_message)


def main():
    """Ana fonksiyon - interaktif chatbot"""
    chatbot = SupportChatbot()
    
    print("=" * 60)
    print("SMSPARK DESTEK CHATBOTU")
    print("=" * 60)
    print("Merhaba! Size nasıl yardımcı olabilirim?")
    print("Çıkmak için 'çıkış' yazın.\n")
    
    while True:
        user_input = input("Kullanıcı: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ['çıkış', 'exit', 'quit', 'q']:
            print("\nİyi günler! Başka bir sorunuzda yine bize ulaşabilirsiniz.")
            break
        
        # Chatbot cevabını al
        response = chatbot.generate_response(user_input)
        
        print(f"\nDestek: {response}\n")


if __name__ == '__main__':
    main()

