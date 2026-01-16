#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gelişmiş Akıllı Destek Chatbotu
Ticket geçmişinden öğrenen, sorun kaynağı analizi yapan, akıllı cevap stratejisi kullanan destek asistanı
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict

class AdvancedSupportChatbot:
    """Gelişmiş ticket analizi ve akıllı cevap stratejisi ile destek chatbotu"""
    
    def __init__(self):
        """Chatbot'u başlatır ve verileri yükler"""
        self.templates = self._load_templates()
        self.keywords = self._extract_keywords()
        self.problem_patterns = self._load_problem_patterns()
        self.context_history = []
        self.repeated_questions = {}  # Tekrar soruları takip et
        
    # ========== 1️⃣ TICKET SINIFLANDIRMA (16 Kategori) ==========
    
    def _normalize_message(self, message: str) -> str:
        """Yazım hatalarını ve alternatif yazımları normalize eder - GELİŞMİŞ NORMALİZASYON"""
        msg = message.lower().strip()
        import re
        
        # Türkçe karakter varyasyonlarını eşle (ç/c, ı/i, ü/u, ö/o, ş/s, ğ/g)
        # Önce Türkçe karakterleri normalize et (kök eşleştirme için)
        turkish_char_map = {
            'ç': 'c', 'ı': 'i', 'ü': 'u', 'ö': 'o', 'ş': 's', 'ğ': 'g',
            'Ç': 'c', 'İ': 'i', 'Ü': 'u', 'Ö': 'o', 'Ş': 's', 'Ğ': 'g'
        }
        # Önce normalizasyon için özel durumları kaydet
        for tr_char, en_char in turkish_char_map.items():
            msg = msg.replace(tr_char, en_char)
        
        # ÖNEMLİ: "hesabim" -> "hesap" dönüşümünü EN BAŞTA yap (kök eşleştirme için)
        # Böylece "hesabimin silinmesini" -> "hesap silinmesini" olur
        msg = msg.replace('hesabimin', 'hesap')
        msg = msg.replace('hesabimi', 'hesap')
        msg = msg.replace('hesabim', 'hesap')
        
        # Çift harf hatalarını düzelt (gelmmıyor -> gelmiyor)
        msg = re.sub(r'gelmm+[iy]?[oy]r?', 'gelmiyor', msg)
        msg = re.sub(r'gelmm+edi', 'gelmedi', msg)
        msg = re.sub(r'yuklenmm+edi', 'yuklenmedi', msg)
        msg = re.sub(r'dusmm+edi', 'dusmedi', msg)
        
        # Yaygın yazım hatalarını düzelt - ÇOK GENİŞ LİSTE
        replacements = {
            # "gelmiyor" varyasyonları
            'gelmiyo': 'gelmiyor', 'gelmiyoru': 'gelmiyor', 'gelmiyorum': 'gelmiyor',
            'gelmıyor': 'gelmiyor', 'gelmıyo': 'gelmiyor', 'gelmediyo': 'gelmedi',
            'gelmediyor': 'gelmedi', 'gelmedim': 'gelmedi', 'gelmıyo': 'gelmiyor',
            
            # "alamıyorum" varyasyonları  
            'alamıyorun': 'alamıyorum', 'alamıyoruz': 'alamıyorum', 'alamıyom': 'alamıyorum',
            'almiyorum': 'alamıyorum', 'alamadim': 'alamadım',
            
            # "olmuyor" varyasyonları
            'olmıyo': 'olmuyor', 'olamıyor': 'olamıyor', 'olamıyorum': 'olamıyor',
            'olamadim': 'olamadım',
            
            # "yüklenmedi" varyasyonları
            'yuklenmedi': 'yuklenmedi', 'yuklenmedim': 'yuklenmedim',
            'yuklenmemis': 'yuklenmedi', 'yuklenmemış': 'yuklenmedi',
            
            # "düşmedi" varyasyonları
            'dusmedi': 'dusmedi', 'dusmedim': 'dusmedim', 'dusmemis': 'dusmedi',
            'dusmemış': 'dusmedi',
            
            # "yatırdım" varyasyonları
            'yatirdim': 'yatirdim', 'yatirdim': 'yatirdim',
            
            # "geçmedi" varyasyonları
            'gecmedi': 'gecmedi', 'gecmedim': 'gecmedim', 'gecmemis': 'gecmedi',
            'hesaba gecmedi': 'hesaba gecmedi', 'hesabima gecmedi': 'hesabima gecmedi',
            
            # "halen/hala" varyasyonları
            'halan': 'halen', 'hala': 'halen', 'halen gelmedi': 'halen gelmedi',
            'hala dusmedi': 'halen dusmedi', 'hala gecmedi': 'halen gecmedi',
            
            # "kısıtlandı" varyasyonları
            'kıtıstlandı': 'kisitlandi', 'kıtıstlandi': 'kisitlandi',
            'kıstılandı': 'kisitlandi', 'kıstılandi': 'kisitlandi',
            'kisitlandi': 'kisitlandi', 'kisitlandim': 'kisitlandi',
            
            # "kapandı" varyasyonları
            'kapandimi': 'kapandi', 'kapandımi': 'kapandi', 'kapandi': 'kapandi',
            'kapandim': 'kapandi',
            
            # Para/ödeme varyasyonları
            'para yukledim': 'para yukledim', 'para yatirdim': 'para yatirdim',
            'para cekildi': 'para cekildi', 'odeme': 'odeme', 'odeme yaptim': 'odeme yaptim',
            'odeme yaptım': 'odeme yaptim', 'odeme yapti': 'odeme yaptim',
            'havalle': 'havale', 'havale yaptim': 'havale', 'havale yaptım': 'havale',
            'havale yapti': 'havale', 'havale gonderdim': 'havale',
            # "atarmısınız" varyasyonları (para transferi talebi)
            'atarmisiniz': 'at', 'atarmısınız': 'at', 'atabilir misiniz': 'at',
            'atabilirmisiniz': 'at', 'atabilirsiniz': 'at',
            # "param" -> "para" normalizasyonu
            'parami': 'para', 'param': 'para',
            
            # "silme/kapatma" varyasyonları
            'silem': 'silme', 'silmek': 'silme', 'silme istiyorum': 'silme',
            'kapatmak': 'kapatma', 'kapatmak istiyorum': 'kapatma',
            'hesap silem': 'hesap silme', 'hesap silmek': 'hesap silme',
            'hesap kapatmak': 'hesap kapatma', 'hesabimi sil': 'hesap silme',
            'hesabimi kapat': 'hesap kapatma', 'hesabimi silebilirmiyim': 'hesap silme',
            # "hesabim" -> "hesap" dönüşümü zaten yukarıda yapıldı, burada sadece kalan ifadeleri normalize et
            'hesap silinmesini': 'hesap silme', 'hesap kapanmasini': 'hesap kapatma',
            'hesap silinmesini talep': 'hesap silme talep',
            'hesap kapanmasini talep': 'hesap kapatma talep',
            
            # Diğer yaygın hatalar
            'yuklemem': 'yuklemem', 'yukleme': 'yukleme',
            'hesabima': 'hesabima', 'hesabima dusmedi': 'hesabima dusmedi',
            'hesabima gecmedi': 'hesabima gecmedi',
        }
        
        # Direkt replacement'ları uygula
        for wrong, correct in replacements.items():
            msg = msg.replace(wrong, correct)
        
        return msg
    
    def classify_ticket_category(self, user_message: str) -> Tuple[str, float]:
        """16 kategoriden birine ticket'ı sınıflandırır"""
        # Mesajı normalize et (yazım hatalarını düzelt)
        user_message_lower = self._normalize_message(user_message)
        
        # Selamlama kontrolü - sadece kısa mesajlar için
        greetings = ['selam', 'selamlar', 'merhaba', 'iyi günler', 'merhabalar', 'sa', 'hey']
        if any(greeting in user_message_lower for greeting in greetings):
            # Eğer sadece selamlama varsa (max 2 kelime) ve sorun belirtisi yoksa
            words = user_message_lower.split()
            if len(words) <= 2 and not any(word in user_message_lower for word in ['kapandı', 'kısıtlandı', 'sorun', 'problem', 'hata', 'gelmiyor', 'alamıyorum']):
                return 'selamlama', 1.0
        
        scores = defaultdict(float)
        categories_found = []  # Multi-intent için - bulunan kategoriler
        
        # ========== ÖNCE ÖDEME/BAKİYE KONTROLÜ (EN ÖNEMLİ - ÖNCE KONTROL ET) ==========
        
        # Ödeme çekildi/yükledim ama yansımadı - EN ÖNCELİKLİ
        # Kök eşleştirme: yatır, yükle, çekil, para att, ödeme yaptım, havale
        has_odeme_keyword = any(root in user_message_lower for root in [
            'yatir', 'yukle', 'cekil', 'para att', 'para yatir', 'para yukle',
            'bakiye yukle', 'bakiye yatir', 'havale', 'eft', 'odeme', 'odeme yaptim',
            'odeme yaptim', 'para gonderdim', 'para gonder', 'para yolladim'
        ])
        has_olumsuz = any(root in user_message_lower for root in [
            'gelmedi', 'dusmedi', 'yansimadi', 'gecmedi', 'yuklenmedi',
            'hesabima dusmedi', 'hesabima gecmedi', 'hesaba dusmedi', 'hesaba gecmedi',
            'hala dusmedi', 'hala gecmedi', 'halen dusmedi', 'halen gecmedi',
            'hesabima dusmemis', 'hesaba gelmemis', 'hesabima gelmemis'
        ])
        
        # "ödeme yaptım havalle hesabıma düşmedi" formatı - ÖNEMLİ
        # "ödeme yaptım" + "havale" + "hesabıma düşmedi" kombinasyonu
        has_odeme_yaptim = 'odeme yaptim' in user_message_lower or 'odeme yaptım' in user_message_lower
        has_havale = 'havale' in user_message_lower or 'havalle' in user_message_lower
        has_hesabima_dusmedi = any(phrase in user_message_lower for phrase in [
            'hesabima dusmedi', 'hesabima gecmedi', 'hesaba dusmedi', 'hesaba gecmedi',
            'hesabima gelmedi', 'hesaba gelmedi'
        ])
        
        # "Paramı acil bi şekilde hesabıma atarmısınız" formatı - ÖNEMLİ
        # "para" + "hesabıma" + "at" kombinasyonu (para transferi talebi)
        has_para = 'para' in user_message_lower or 'param' in user_message_lower or 'parami' in user_message_lower
        has_hesabima = 'hesabima' in user_message_lower or 'hesaba' in user_message_lower
        has_at = any(root in user_message_lower for root in [
            'at', 'atarmisiniz', 'atarmısınız', 'atabilir misiniz', 'atabilirmisiniz',
            'yukleyin', 'yukleyin', 'yansitin', 'yansıtın', 'yansit'
        ])
        has_acil = 'acil' in user_message_lower or 'acilen' in user_message_lower
        
        # "Paramı hesabıma atarmısınız" veya "acil para" formatı
        if (has_para and has_hesabima and has_at) or \
           (has_para and has_acil) or \
           (has_para and has_hesabima and has_acil):
            return 'ozel_talep_whatsapp_odeme', 1.0  # Direkt WhatsApp'a yönlendir
        
        # "ödeme yaptım havalle hesabıma düşmedi" formatı
        if (has_odeme_yaptim and has_havale and has_hesabima_dusmedi) or \
           (has_odeme_yaptim and has_olumsuz) or \
           (has_havale and has_hesabima_dusmedi):
            return 'ozel_talep_whatsapp_odeme', 1.0  # Direkt WhatsApp'a yönlendir
        
        # "X TL yatırdım ama hesabıma düşmedi" formatı
        has_tl_yatirdim = ('tl' in user_message_lower or 'lira' in user_message_lower) and \
                         (has_odeme_keyword or 'yatir' in user_message_lower or 'yukle' in user_message_lower)
        
        if (has_odeme_keyword and has_olumsuz) or (has_tl_yatirdim and has_olumsuz):
            categories_found.append(('odeme_yuklenmedi', 50))  # En yüksek skor
            return 'ozel_talep_whatsapp_odeme', 1.0  # Direkt WhatsApp'a yönlendir
        
        # ========== İADE TALEBİ KONTROLÜ (2. ÖNCELİK) ==========
        has_iade_talebi = any(root in user_message_lower for root in [
            'iade', 'geri', 'geri odeme', 'geri ver', 'parami geri', 'para iadesi',
            'ucret iadesi', 'iptal iade', 'refund'
        ])
        if has_iade_talebi:
            categories_found.append(('iade', 40))
        
        # ========== SMS GELMİYOR KONTROLÜ ==========
        has_sms_keyword = any(root in user_message_lower for root in [
            'sms', 'kod', 'otp', 'onay', 'dogrulama', 'mesaj', 'arama'
        ])
        has_sms_olumsuz = any(root in user_message_lower for root in [
            'gelm', 'alam', 'olm', 'calism', 'gelmedi', 'gelmiyo', 'olamadi'
        ])
        has_bekleme = any(phrase in user_message_lower for phrase in [
            'saat sonra', 'tekrar dene', 'deneyin', 'bekle', 'bekleyin'
        ])
        
        if has_sms_keyword and (has_sms_olumsuz or has_bekleme):
            categories_found.append(('sms_gelmiyor', 35))
        
        # Eğer hem SMS gelmiyor hem de iade talebi varsa -> İade talebine öncelik ver
        if has_iade_talebi and has_sms_keyword and has_sms_olumsuz:
            return 'ozel_talep_iade_genel', 1.0
        
        # 1. SMS gelmiyor - EN YAYGIN SORUN (öncelikli) - Çok esnek eşleştirme
        # "gelm", "alam", "olm" kelimesi varsa ve SMS/kod/mesaj/doğrulama ile ilgiliyse
        has_sms_keyword = any(word in user_message_lower for word in [
            'sms', 'kod', 'onay', 'doğrulama', 'mesaj', 'numara', 'doğrulama'
        ])
        has_gelm = 'gelm' in user_message_lower
        has_alam = 'alam' in user_message_lower
        has_olm = 'olm' in user_message_lower  # "olmuyor", "olamıyor" için
        
        # Negatif kelimeler var mı kontrol et (çok geniş kapsam)
        negative_words = [
            'gelmiyor', 'gelmedi', 'gelmiyo', 'gelmedim', 'gelmmıyor',
            'alamıyorum', 'alamadım', 'alamıyorun', 'alamıyom',
            'gelmiyorum', 'gelmıyor', 'gelmiyoru',
            'olmuyor', 'olamıyor', 'olamıyorum', 'olmadı', 'olamadım',
            'çalışmıyor', 'calışmıyor', 'çalışmıyor', 'çalışmıyo'
        ]
        has_negative = any(neg in user_message_lower for neg in negative_words)
        
        # "SMS ile doğrulama olmuyor", "23 saat sonra tekrar deneyin" gibi
        has_bekleme = any(phrase in user_message_lower for phrase in [
            '23 saat', '24 saat', 'tekrar deneyin', 'bekle', 'bekleyin',
            'sonra tekrar', 'saat sonra', 'bekleme', 'deneyin diyor'
        ])
        
        # "mesaj gelmiyor", "numara mesaj gelmiyor", "SMS ile doğrulama olmuyor" gibi
        # Bekleme süresi belirtilmişse de SMS sorunu sayılır
        if (has_sms_keyword and (has_gelm or has_alam or has_olm) and has_negative) or \
           (has_sms_keyword and has_bekleme) or \
           ('numara' in user_message_lower and has_gelm and has_negative) or \
           ('mesaj' in user_message_lower and has_gelm and has_negative) or \
           ('doğrulama' in user_message_lower and has_olm and has_negative):
            # İade talebi yoksa SMS sorunu olarak işaretle
            if not has_iade_talebi:
                scores['sms_gelmiyor'] += 35  # Çok yüksek öncelik - en yaygın sorun
        
        # 2. WhatsApp doğrulama sorunu
        if any(phrase in user_message_lower for phrase in [
            'whatsapp doğrulama', 'whatsapp kod', 'wp doğrulama', 'whatsapp sms',
            'whatsapp hesabım', 'wp hesabım'
        ]):
            scores['whatsapp_dogrulama'] += 18
        
        # 3. Telegram doğrulama sorunu
        if any(phrase in user_message_lower for phrase in [
            'telegram doğrulama', 'telegram kod', 'tg doğrulama', 'telegram sms',
            'telegram hesabım', 'tg hesabım'
        ]):
            scores['telegram_dogrulama'] += 18
        
        # 4. Cihaz/IP ban sorunu
        if any(phrase in user_message_lower for phrase in [
            'cihaz ban', 'ip ban', 'cihaz engellendi', 'ip engellendi',
            'geçici yasak', 'mimlenmiş', 'kara liste'
        ]):
            scores['cihaz_ip_ban'] += 16
        
        # 5. Stok yok hatası
        if any(phrase in user_message_lower for phrase in [
            'stok yok', 'stok bulunmuyor', 'numara bulunmuyor', 'stok sorunu'
        ]):
            scores['stok_yok'] += 14
        
        # 6. Yanlış numara satın alma
        if any(phrase in user_message_lower for phrase in [
            'yanlış numara', 'hatalı numara', 'geçersiz numara', 'numara çalışmıyor'
        ]):
            scores['yanlis_numara'] += 12
        
        # 7. Para iadesi talebi - ÖNEMLİ: Detaylı algılama
        # Direkt iade talepleri
        if any(phrase in user_message_lower for phrase in [
            'para iadesi', 'iade istiyorum', 'paramı geri ver', 'para geri',
            'bakiye iadesi', 'iade talep', 'paramı iade et', 'ücret iadesi',
            'iade istiyoruz', 'iade edin', 'geri ver', 'geri ödeme',
            'para iade', 'iade yap', 'iade yapın'
        ]):
            scores['para_iadesi'] += 25  # Yüksek öncelik
        
        # Kombinasyon durumları: SMS geldi + 2FA açık + iade
        has_sms_geldi = any(word in user_message_lower for word in [
            'sms geldi', 'sms geldim', 'sms aldım', 'sms aldim',
            'kod geldi', 'kod geldim', 'kod aldım', 'kod aldim',
            'onay kodu geldi', 'doğrulama geldi'
        ])
        has_2fa = any(phrase in user_message_lower for phrase in [
            'iki aşamalı', 'iki aşama', '2fa', '2 aşama', 'iki faktör',
            'doğrulama açık', 'doğrulama açılmış', 'doğrulama açikmiş',
            'doğrulama açıldı', 'doğrulama açildi', 'doğrulama aktif',
            '2 aşamalı doğrulama', 'iki faktörlü', 'iki aşamalı doğrulama',
            'açıkmış', 'açikmiş', 'açıldı', 'açildi'
        ])
        has_iade_keyword = any(word in user_message_lower for word in [
            'iade', 'geri', 'ücret iadesi', 'para iadesi', 'geri ödeme',
            'iade istiyorum', 'iade yap', 'geri ver'
        ])
        
        # SMS geldi + 2FA açık + iade talebi = Özel durum
        if has_sms_geldi and has_2fa and has_iade_keyword:
            return 'ozel_talep_iade_2fa', 1.0
        
        # SMS geldi + iade talebi (genel)
        if has_sms_geldi and has_iade_keyword:
            return 'ozel_talep_iade_genel', 1.0
        
        # 8. Bakiye yükleme sorunu - ÖNEMLİ: WhatsApp'a yönlendir
        # Ödeme/para yükleme sorunları - WhatsApp desteği gerekli
        # Esnek algılama: "para yükledim", "çekildi" ve "yüklenmedi"/"gelmedi" birlikte varsa
        
        # "Para yükledim" formatı - ÖNEMLİ
        has_para_yukledim = any(phrase in user_message_lower for phrase in [
            'para yükledim', 'para yukledim', 'para yukledım',
            'para yükledım', 'para yükledi', 'bakiye yükledim',
            'para yatırdım', 'para yatirdim', 'bakiye yatırdım'
        ])
        has_halen_gelmedi = any(phrase in user_message_lower for phrase in [
            'halan gelmedi', 'halen gelmedi', 'hala gelmedi',
            'hala yansımadı', 'halan yansımadı', 'halen yansımadı'
        ])
        
        # "Para yükledim halen gelmedi" formatı
        if has_para_yukledim and has_halen_gelmedi:
            return 'ozel_talep_whatsapp_odeme', 1.0
        
        # "Para yükledim" + "gelmedi" kombinasyonu
        if has_para_yukledim and ('gelmedi' in user_message_lower or 'yansımadı' in user_message_lower):
            return 'ozel_talep_whatsapp_odeme', 1.0
        
        # Esnek algılama: "çekildi" ve "yüklenmedi"/"gelmedi" birlikte varsa
        has_cekilme = any(word in user_message_lower for word in [
            'çekildi', 'cekildi', 'çekildim', 'cekildim'
        ])
        has_yuklenmedi = any(word in user_message_lower for word in [
            'yüklenmedi', 'yuklenmedi', 'yüklenmedim', 'yuklenmedim',
            'gelmedi', 'gelmedim', 'yansımadı', 'yansimadi', 'yansımadim', 'yansimadim'
        ])
        has_tl = 'tl' in user_message_lower or 'türk lirası' in user_message_lower
        
        # "X tl çekildi yüklenmedi" formatı
        if (has_cekilme and has_yuklenmedi) or (has_tl and has_cekilme and has_yuklenmedi):
            return 'ozel_talep_whatsapp_odeme', 1.0
        
        # "yatırdım ama hesabıma düşmedi" kombinasyonu - ÖNEMLİ
        has_yatirdim = any(phrase in user_message_lower for phrase in [
            'yatırdım', 'yatirdim', 'yatırdim', 'yatirdım',
            'yükledim', 'yukledim', 'para attım', 'para attim',
            'para yatırdım', 'para yatirdim', 'havale yaptım', 'havale yaptim',
            'eft yaptım', 'eft yaptim'
        ])
        has_hesaba_dusmedi = any(phrase in user_message_lower for phrase in [
            'hesabıma düşmedi', 'hesabima dusmedi', 'hesabıma geçmedi',
            'hesabima gecmedi', 'hesaba geçmedi', 'hesaba gecmedi',
            'hesaba düşmedi', 'hesaba dusmedi', 'hala düşmedi', 'hala dusmedi',
            'hala geçmedi', 'hala gecmedi', 'gelmedi', 'yansımadı', 'yansimadi'
        ])
        
        # "X TL yatırdım ama hesabıma düşmedi" formatı
        if has_yatirdim and has_hesaba_dusmedi:
            return 'ozel_talep_whatsapp_odeme', 1.0
        
        # Diğer ödeme sorunları
        if any(phrase in user_message_lower for phrase in [
            'bakiye gelmedi', 'para gelmedi', 'bakiye yükleme', 'para yatırma',
            'bakiye yüklenmedi', 'hesaba geçmedi', 'para yansımadı',
            'ödeme yansımadı', 'havale yaptım gelmedi', 'havaleden para attım gelmedi',
            'iban attım gelmedi', 'iban dan atım gelmedi', 'eft yaptım gelmedi',
            'para çekildi yüklenmedi', 'çekildi yüklenmedi', 'çekildi gelmedi',
            'tl çekildi', 'yatırdım gelmedi', 'para attım gelmedi', 'para çekildi',
            'yükleme yapmadı', 'yükleme yapmadi', 'yüklenmedi hesaba',
            'tl yatırdım', 'yatırdım hesaba', 'para düşmedi', 'para dusmedi'
        ]):
            # WhatsApp desteğine yönlendir (öncelikli)
            return 'ozel_talep_whatsapp_odeme', 1.0
        
        # 9. Ödeme bildirimi yapılmamış
        if any(phrase in user_message_lower for phrase in [
            'ödeme bildirimi', 'ödeme yaptım', 'para yatırdım', 'havale yaptım',
            'eft yaptım', 'ödeme bildirmedim'
        ]):
            scores['odeme_bildirimi'] += 12
        
        # 10. SMS kodu geçersiz / süresi doldu
        if any(phrase in user_message_lower for phrase in [
            'kod geçersiz', 'kod süresi doldu', 'kod süresi bitti', 'kod hatalı',
            'kod yanlış', 'kod giremiyorum'
        ]):
            scores['sms_kodu_gecersiz'] += 11
        
        # 11. Hesap askıya alındı
        if any(phrase in user_message_lower for phrase in [
            'hesap kapandı', 'hesabım kapandı', 'hesap kapatıldı', 'hesap kısıtlandı',
            'hesap engellendi', 'hesap yasaklandı', 'numara kapandı', 'numaram kapandı',
            'aldığım numara kapandı', 'numaram kısıtlandı', 'hesabım kısıtlandı',
            'spam yedi', 'ban yedi', 'yasak', 'engellendi'
        ]):
            scores['hesap_askiya'] += 25  # Çok yüksek skor
        
        # 12. Numara tekrar kullanılmak isteniyor / Numara alamıyorum
        if any(phrase in user_message_lower for phrase in [
            'numara tekrar', 'aynı numara', 'numara kullanılıyor', 'numara tek kullanım',
            'numara kalıcı', 'numara süre', 'numara kaç gün'
        ]):
            scores['numara_tekrar'] += 10
        
        # NUMARA ALAMIYORUM - ÖNEMLİ KATEGORİ - Esnek eşleştirme
        has_numara = 'numara' in user_message_lower
        has_alam = 'alam' in user_message_lower
        has_bulam = 'bulam' in user_message_lower
        has_yok = 'yok' in user_message_lower and 'numara' in user_message_lower
        
        if has_numara and (has_alam or has_bulam or has_yok):
            # Negatif kelimeler var mı kontrol et
            negative_words = ['alamıyorum', 'alamadım', 'alamıyorun', 'alamıyom', 
                            'bulamıyorum', 'bulamıyom', 'yok']
            if any(neg in user_message_lower for neg in negative_words):
                scores['numara'] += 22  # Yüksek skor
        
        # 13. 2FA kurulumu sorunu - Detaylı algılama
        has_2fa_keywords = any(phrase in user_message_lower for phrase in [
            '2fa', 'iki faktörlü', 'doğrulama kurulumu', '2fa kurulumu',
            '2 aşamalı', 'iki aşamalı', 'iki aşama', '2 aşama',
            'iki aşamalı doğrulama', '2 aşamalı doğrulama'
        ])
        has_sinirsiz = any(word in user_message_lower for word in [
            'sınırsız', 'sinirsiz', 'sınırsız kullan', 'kalıcı', 'kalici',
            'tekrar kullan', 'sürekli kullan', 'surekli kullan'
        ])
        
        # 2FA + sınırsız kullanım sorusu
        if has_2fa_keywords and has_sinirsiz:
            return 'numara_tekrar', 1.0  # Numara tekrar kullanım / kalıcılık
        
        # Sadece 2FA kurulumu
        if has_2fa_keywords:
            scores['2fa_kurulumu'] += 15  # Yüksek öncelik
        
        # 14. VPN / ülke uyumsuzluğu
        if any(phrase in user_message_lower for phrase in [
            'vpn', 'ülke uyumsuz', 'vpn kullanmalı', 'vpn gerekli'
        ]):
            scores['vpn_ulke_uyumsuz'] += 8
        
        # 15. Sistem hatası iddiası
        if any(phrase in user_message_lower for phrase in [
            'sistem hatası', 'site hatası', 'platform hatası', 'hata var',
            'çalışmıyor', 'bug var'
        ]):
            scores['sistem_hatasi'] += 7
        
        # 16. Kullanıcı hatası kaynaklı problemler
        if any(phrase in user_message_lower for phrase in [
            'yanlış girdim', 'hatalı girdim', 'yanlış yaptım', 'benim hatam'
        ]):
            scores['kullanici_hatasi'] += 6
        
        # ÖZEL TALEPLER - Destek sistemine yönlendirilmeli
        # Hesap kapatma/silme talepleri - GENİŞLETİLMİŞ ALGILAMA
        has_hesap = any(root in user_message_lower for root in [
            'hesap', 'hesabim', 'hesabimin', 'hesabimi'
        ])
        has_silme = any(root in user_message_lower for root in [
            'sil', 'silme', 'silmek', 'silem', 'silinmesini', 'silebilirmiyim',
            'silinmesini talep', 'silinmesini onay'
        ])
        has_kapatma = any(root in user_message_lower for root in [
            'kapat', 'kapatmak', 'kapatma', 'kapanmasini', 'kapatalim'
        ])
        has_talep = any(root in user_message_lower for root in [
            'talep', 'istiyorum', 'istiyoruz', 'ediyorum', 'ediyoruz', 'onayliyorum',
            'onay', 'talep ediyorum'
        ])
        
        # "hesap silme/kapatma" kombinasyonu - ÇOK ESNEK
        # "hesabimin silinmesini talep ediyorum" gibi uzun ifadeleri yakala
        if has_hesap and (has_silme or has_kapatma):
            return 'ozel_talep_hesap_kapatma', 1.0
        
        # Eski yöntem (fallback) - daha spesifik ifadeler
        if any(phrase in user_message_lower for phrase in [
            'hesabim kapatmak', 'hesabim silmek', 'hesap kapatmak istiyorum',
            'hesap silmek istiyorum', 'hesabi kapat', 'hesabi sil',
            'hesabim kapatalim', 'hesabi kapatalim', 'hesap silme',
            'hesap kapatma', 'hesabimin silinmesini', 'hesabimin kapanmasini',
            'hesabimin silinmesini talep', 'hesabimin kapanmasini talep',
            'hesabimin silinmesini talep ediyorum', 'hesabimin kapanmasini talep ediyorum',
            'hesabimin silinmesini onayliyorum', 'hesabimin kapanmasini onayliyorum'
        ]):
            return 'ozel_talep_hesap_kapatma', 1.0
        
        # Özel numara talepleri (Türkiye, spesifik ülke vb.)
        if any(phrase in user_message_lower for phrase in [
            'türkiye numarası', 'turkiye numarası', 'tr numarası',
            'türkiye numara almak', 'turkiye numara almak',
            'türkiye numarası istiyorum', 'özel numara', 'belirli numara',
            'şu ülke numarası', 'bu ülke numarası', 'spesifik numara'
        ]):
            return 'ozel_talep_numara', 1.0
        
        # Diğer özel talepler (iş birliği, toplu alım, özel fiyat vb.)
        if any(phrase in user_message_lower for phrase in [
            'iş birliği', 'toplu alım', 'toplu numara', 'çoğul numara',
            'özel fiyat', 'indirim', 'kampanya', 'anlaşma',
            'kurumsal', 'firma', 'şirket', 'toptan'
        ]):
            return 'ozel_talep_genel', 1.0
        
        # Multi-intent: Eğer birden fazla kategori bulunduysa, en yüksek öncelikliden başla
        if categories_found:
            # Öncelik sırasına göre sırala
            categories_found.sort(key=lambda x: x[1], reverse=True)
            best_category = categories_found[0][0]
            
            # Eğer iade + SMS varsa, iade'ye öncelik ver ama SMS'yi de ele al
            if len(categories_found) > 1 and 'iade' in [c[0] for c in categories_found] and \
               'sms_gelmiyor' in [c[0] for c in categories_found]:
                return 'ozel_talep_iade_genel', 1.0  # İade öncelikli
            
            return best_category, 1.0
        
        # En yüksek skorlu kategoriyi döndür (fallback)
        if scores:
            best_category = max(scores.items(), key=lambda x: x[1])
            confidence = min(best_category[1] / 30.0, 1.0)
            if best_category[1] >= 5:  # Çok düşük threshold
                if best_category[0] == 'sms_gelmiyor' and best_category[1] >= 25:
                    return 'sms_gelmiyor', 1.0
                return best_category[0], confidence
        
        # ASLA CEVAPSIZ BIRAKMA - En kötü ihtimalle genel soru sor
        # Çok kısa mesajlar için (örn: "olmuyor", "gelmedi", "yok")
        if len(user_message_lower.split()) <= 3:
            if any(root in user_message_lower for root in ['gelm', 'olm', 'calism', 'yok']):
                return 'sms_gelmiyor', 0.6  # En olası kategori
            if any(root in user_message_lower for root in ['yatir', 'yukle', 'odeme']):
                return 'ozel_talep_whatsapp_odeme', 0.6
        
        # Son çare: Genel bilgi talebi
        return 'genel_bilgi', 0.3
    
    # ========== 2️⃣ SORUN KAYNAĞI ANALİZİ ==========
    
    def analyze_problem_source(self, user_message: str, category: str) -> str:
        """Sorunun kaynağını belirler"""
        user_lower = user_message.lower()
        
        # Kullanıcı hatası
        if any(word in user_lower for word in ['yanlış girdim', 'hatalı girdim', 'benim hatam', 'yanlış yaptım']):
            return 'kullanici_hatasi'
        
        # Cihaz banı
        if any(word in user_lower for word in ['cihaz', 'telefon', 'mimlenmiş', 'cihaz ban']):
            if 'ban' in user_lower or 'engel' in user_lower:
                return 'cihaz_bani'
        
        # IP banı
        if any(word in user_lower for word in ['ip', 'internet', 'ip ban', 'ip engel']):
            return 'ip_bani'
        
        # VPN uyumsuzluğu
        if 'vpn' in user_lower and ('kullanmıyorum' in user_lower or 'kullanmadım' in user_lower):
            return 'vpn_uyumsuzlugu'
        
        # Spam şüphesi
        if any(word in user_lower for word in ['spam', 'çok mesaj', 'aşırı mesaj']):
            return 'spam_suphesi'
        
        # Kod süresi dolmuş
        if any(word in user_lower for word in ['süre doldu', 'süresi bitti', 'geç kaldım']):
            return 'kod_suresi_dolmus'
        
        # Stok problemi
        if 'stok' in user_lower:
            return 'stok_problemi'
        
        # Yanlış kategori seçimi
        if any(word in user_lower for word in ['kaliteli değil', 'ucuz numara', 'yanlış kategori']):
            return 'yanlis_kategori'
        
        # Numara sağlayıcı kaynaklı
        if any(word in user_lower for word in ['numara sağlayıcı', 'operatör', 'sağlayıcı']):
            return 'numara_saglayici'
        
        # Varsayılan: Uygulama kaynaklı engel
        if category in ['hesap_askiya', 'whatsapp_dogrulama', 'telegram_dogrulama']:
            return 'uygulama_kaynakli_engel'
        
        return 'belirsiz'
    
    # ========== 3️⃣ DUYGU ANALİZİ (Öfkeli Kullanıcı Tespiti) ==========
    
    def detect_user_emotion(self, user_message: str) -> Tuple[str, float]:
        """Kullanıcının duygusal durumunu tespit eder"""
        user_lower = user_message.lower()
        
        # Öfkeli kelimeler
        angry_words = ['rezillik', 'saçmalık', 'berbat', 'kötü', 'kötü hizmet', 
                       'şikayet', 'dava', 'sizden nefret', 'çok kötü', 'berbat',
                       'para veriyorum', 'iade istiyorum', 'paramı geri ver',
                       'çalışmıyor', 'aldatma', 'dolandırıcı']
        
        # Acil durum kelimeleri
        urgent_words = ['acil', 'hemen', 'şimdi', 'derhal', 'ivedilikle', 'çok acil']
        
        angry_score = sum(1 for word in angry_words if word in user_lower)
        urgent_score = sum(1 for word in urgent_words if word in user_lower)
        
        if angry_score >= 2:
            return 'angry', 0.9
        elif angry_score >= 1:
            return 'frustrated', 0.7
        elif urgent_score >= 1:
            return 'urgent', 0.6
        
        return 'normal', 0.3
    
    # ========== 4️⃣ TEKRAR SORU TESPİTİ ==========
    
    def is_repeated_question(self, user_message: str) -> bool:
        """Aynı sorunun tekrar sorulup sorulmadığını kontrol eder"""
        if len(self.context_history) < 2:
            return False
        
        # Son 3 mesajı kontrol et
        recent_messages = self.context_history[-3:]
        user_lower = user_message.lower()
        
        # Benzer kelimeler sayısı
        for prev_msg in recent_messages:
            prev_lower = prev_msg.lower()
            common_words = set(user_lower.split()) & set(prev_lower.split())
            if len(common_words) >= 3:  # 3+ ortak kelime varsa tekrar soru olabilir
                return True
        
        return False
    
    # ========== 5️⃣ GELİŞMİŞ CEVAP ÜRETİMİ ==========
    
    def generate_advanced_response(self, user_message: str) -> str:
        """Gelişmiş cevap stratejisi ile cevap üretir"""
        # Context'e ekle
        self.context_history.append(user_message)
        
        # 1. Duygu analizi
        emotion, emotion_score = self.detect_user_emotion(user_message)
        
        # 2. Tekrar soru kontrolü
        is_repeated = self.is_repeated_question(user_message)
        
        # 3. Kategori belirleme
        category, confidence = self.classify_ticket_category(user_message)
        
        # 4. Sorun kaynağı analizi
        problem_source = self.analyze_problem_source(user_message, category)
        
        # 5. Öfkeli kullanıcı için özel yaklaşım
        if emotion == 'angry':
            return self._handle_angry_user(user_message, category, problem_source)
        
        # 6. Tekrar soru için kısa cevap
        if is_repeated:
            return self._handle_repeated_question(category)
        
        # 7. Normal cevap üretimi
        return self._generate_category_response(category, problem_source, user_message, confidence)
    
    def _handle_angry_user(self, user_message: str, category: str, problem_source: str) -> str:
        """Öfkeli kullanıcıyı sakinleştiren cevap"""
        response = "Merhaba. Durumunuzu anlıyorum ve sorununuzu çözmek için buradayım. "
        
        if category == 'para_iadesi':
            response += "Numara alımı sonrası hizmet başlamış sayıldığı için kart/banka iadesi yapılamamaktadır. Ancak kullanılmayan bakiye hesabınızda kalmaktadır. Dilerseniz farklı numara deneyebilirsiniz."
        elif category == 'sms_gelmiyor':
            response += "SMS gelmeme sorununuz için lütfen şu adımları deneyin:\n\n"
            response += "1️⃣ Cihazınızı 24 saat dinlendirin\n"
            response += "2️⃣ Sadece telefon uygulamasından giriş yapın\n"
            response += "3️⃣ Kaliteli numara seçin\n"
            response += "4️⃣ VPN ile ülke eşleştirin\n\n"
            response += "Numara gelmezse iptal edebilirsiniz, bakiye otomatik iade olur."
        else:
            response += "Sorununuzu daha iyi anlayabilmem için biraz daha detay verebilir misiniz?"
        
        return response
    
    def _handle_repeated_question(self, category: str) -> str:
        """Tekrar soru için kısa cevap"""
        if category == 'sms_gelmiyor':
            return "SMS gelmiyor sorunu için: Cihazı 24 saat dinlendirin, telefon uygulamasından kayıt olun, kaliteli numara seçin. Detaylı bilgi için önceki mesajıma bakabilirsiniz."
        elif category == 'hesap_askiya':
            return "Hesap kapandı sorunu için: 24 saat sonra mesaj gönderin, WhatsApp Business kullanmayın, spam yapmayın. SMS kodu geldikten sonra platform sorumluluk kabul etmez."
        else:
            return "Daha önce verdiğim bilgileri kontrol edebilir misiniz? Hala sorun devam ediyorsa, hangi adımda takıldığınızı belirtir misiniz?"
    
    def _generate_category_response(self, category: str, problem_source: str, user_message: str, confidence: float) -> str:
        """Kategoriye göre detaylı cevap üretir"""
        
        # Selamlama
        if category == 'selamlama':
            return "Merhaba! SMSPark destek ekibine hoş geldiniz. Size nasıl yardımcı olabilirim? Lütfen sorununuzu kısaca açıklayabilir misiniz?\n\nÖrnek sorunlar:\n- SMS/Kod gelmiyor\n- Bakiye/Ödeme sorunu\n- Numara alamıyorum\n- Hesap/Numara kapandı veya kısıtlandı\n- Stok yok"
        
        # SMS gelmiyor
        if category == 'sms_gelmiyor':
            return self._response_sms_gelmiyor(problem_source)
        
        # WhatsApp doğrulama
        if category == 'whatsapp_dogrulama':
            return self._response_whatsapp_dogrulama(problem_source)
        
        # Telegram doğrulama
        if category == 'telegram_dogrulama':
            return self._response_telegram_dogrulama(problem_source)
        
        # Cihaz/IP ban
        if category == 'cihaz_ip_ban':
            return self._response_cihaz_ip_ban()
        
        # Stok yok
        if category == 'stok_yok':
            return self._response_stok_yok()
        
        # Para iadesi
        if category == 'para_iadesi':
            return self._response_para_iadesi()
        
        # Numara alamıyorum
        if category == 'numara':
            return self._response_numara_alamiyorum()
        
        # Bakiye yükleme
        if category == 'bakiye_yukleme':
            return self._response_bakiye_yukleme()
        
        # Ödeme bildirimi
        if category == 'odeme_bildirimi':
            return self._response_odeme_bildirimi()
        
        # SMS kodu geçersiz
        if category == 'sms_kodu_gecersiz':
            return self._response_sms_kodu_gecersiz()
        
        # Hesap askıya alındı
        if category == 'hesap_askiya':
            return self._response_hesap_askiya()
        
        # Numara tekrar kullanım
        if category == 'numara_tekrar':
            return self._response_numara_tekrar()
        
        # 2FA kurulumu
        if category == '2fa_kurulumu':
            return self._response_2fa_kurulumu()
        
        # VPN/ülke uyumsuzluğu
        if category == 'vpn_ulke_uyumsuz':
            return self._response_vpn_ulke_uyumsuz()
        
        # Sistem hatası
        if category == 'sistem_hatasi':
            return self._response_sistem_hatasi()
        
        # Özel talepler - Destek sistemine yönlendirme
        if category == 'ozel_talep_hesap_kapatma':
            return "Merhaba. Hesap kapatma talebiniz için destek sistemimize yönlendiriliyorsunuz.\n\nLütfen aşağıdaki adımları takip edin:\n\n1️⃣ Destek bilet sistemi üzerinden yeni bir talep oluşturun\n2️⃣ \"Hesap Kapatma\" konusunu seçin\n3️⃣ Talebinizi detaylı olarak açıklayın\n\nDestek ekibimiz en kısa sürede talebinizi değerlendirecektir.\n\n⚠️ Hesap kapatma işlemi geri alınamaz. Lütfen bu işlemden emin olduğunuzu belirtin."
        
        if category == 'ozel_talep_numara':
            return "Merhaba. Özel numara talebiniz (örn: Türkiye numarası) için destek sistemimize yönlendiriliyorsunuz.\n\nLütfen aşağıdaki adımları takip edin:\n\n1️⃣ Destek bilet sistemi üzerinden yeni bir talep oluşturun\n2️⃣ \"Özel Numara Talebi\" veya \"Stok Sorunu\" konusunu seçin\n3️⃣ İstediğiniz numara tipini (ülke, kategori, özellikler) detaylı olarak belirtin\n\nDestek ekibimiz talebinizi incelip size özel olarak bilgilendirme yapacaktır.\n\n💡 Not: Bazı ülkeler veya numara türleri stok durumuna göre mevcut olmayabilir."
        
        if category == 'ozel_talep_genel':
            return "Merhaba. Talebiniz için destek sistemimize yönlendiriliyorsunuz.\n\nLütfen aşağıdaki adımları takip edin:\n\n1️⃣ Destek bilet sistemi üzerinden yeni bir talep oluşturun\n2️⃣ Talebinizin uygun olduğu konuyu seçin\n3️⃣ Talebinizi detaylı olarak açıklayın\n\nDestek ekibimiz en kısa sürede talebinizi değerlendirecektir.\n\n💡 İş birliği, toplu alım, özel fiyatlandırma gibi özel talepler için destek ekibimizle iletişime geçmeniz gerekmektedir."
        
        # Ödeme/Bakiye yükleme sorunu - WhatsApp desteği
        if category == 'ozel_talep_whatsapp_odeme':
            return "Merhaba. Ödeme/Bakiye yükleme sorununuz için WhatsApp destek hattımızla iletişime geçmeniz gerekmektedir.\n\n📱 **WhatsApp Destek Hattı:**\n\n**0543 726 59 86**\n\n🔧 **Ne Yapmalısınız:**\n\n1️⃣ Yukarıdaki WhatsApp butonuna tıklayarak destek hattımıza ulaşın\n2️⃣ Veya WhatsApp'tan **05437265986** numarasına yazın\n3️⃣ Ödeme bilgilerinizi hazır bulundurun:\n   - Ödeme tarihi ve saati\n   - Gönderen isim (IBAN'tan gönderildiyse)\n   - İşlem tutarı\n   - Dekont veya ekran görüntüsü (varsa)\n\n💡 **Neden WhatsApp?**\n\nÖdeme ve bakiye işlemleri kişisel bilgiler içerdiği için güvenli bir kanal olan WhatsApp üzerinden hızlıca çözülebilir.\n\n⚠️ Ödeme bildirimi yapmadan ödeme yaptıysanız, destek ekibimiz bildirimi sizin yerinize yapabilir."
        
        # Özel iade talepleri - 2FA açık durumu
        if category == 'ozel_talep_iade_2fa':
            return "Merhaba. İade talebiniz için destek sistemimize yönlendiriliyorsunuz.\n\n📋 **Sorunun Nedeni:**\n\nSMS kodu geldiğinde ve numara aktif edildiğinde hizmet başlamış sayılır. İki aşamalı doğrulama (2FA) açık olması durumunda, numara kullanılmış kabul edilir.\n\n⚠️ **ÖNEMLİ:**\n\n• SMS kodu alındıktan sonra kart/banka iadesi yapılamamaktadır\n• Numara sağlayıcı ücret keser, bu nedenle iade mümkün değildir\n• Kullanılmayan bakiye hesabınızda kalmaktadır\n• Bu bilgi kullanıcı sözleşmemizde belirtilmektedir\n\n🔧 **Ne Yapmalısınız:**\n\n1️⃣ Destek bilet sistemi üzerinden \"Para İadesi\" konulu yeni bir talep oluşturun\n2️⃣ Durumunuzu detaylı olarak açıklayın (2FA açık olduğunu, SMS geldiğini belirtin)\n3️⃣ Ekran görüntüsü veya kanıt varsa paylaşın\n\nDestek ekibimiz talebinizi inceleyip size bilgilendirme yapacaktır."
        
        # Özel iade talepleri - Genel durum
        if category == 'ozel_talep_iade_genel':
            return "Merhaba. İade talebiniz için destek sistemimize yönlendiriliyorsunuz.\n\n📋 **Genel İade Politikası:**\n\n• SMS kodu alındıktan ve numara aktif edildikten sonra hizmet başlamış sayılır\n• Numara alımı sonrası kart/banka iadesi yapılamamaktadır\n• Kullanılmayan bakiye hesabınızda kalmaktadır\n• Dilerseniz farklı numara deneyebilirsiniz\n\n⚠️ **Not:** Numara sağlayıcı ücret keser, bu nedenle iade mümkün değildir. Bu bilgi kullanıcı sözleşmemizde belirtilmektedir.\n\n🔧 **Ne Yapmalısınız:**\n\n1️⃣ Destek bilet sistemi üzerinden \"Para İadesi\" konulu yeni bir talep oluşturun\n2️⃣ Durumunuzu ve iade talebinizin nedenini detaylı olarak açıklayın\n3️⃣ Ekran görüntüsü veya kanıt varsa paylaşın\n\nDestek ekibimiz talebinizi inceleyip size bilgilendirme yapacaktır."
        
        # Genel bilgi talebi (son çare - ASLA CEVAPSIZ KALMA)
        if category == 'genel_bilgi':
            return """Merhaba! SMSPark destek ekibine hoş geldiniz. Size yardımcı olabilmem için sorununuzu biraz daha detaylandırabilir misiniz?

📋 **En Sık Karşılaşılan Sorunlar ve Çözüm Önerileri:**

🔹 **SMS/Kod Gelmiyor:**
   • Bekleme süresi (23-24 saat) varsa belirtilen süreyi bekleyin
   • "Numaralarım" ekranını 10-15 saniye aralıklarla yenileyin
   • Kod gelmiyorsa iptal → başka numara deneyin (iptalde bakiye otomatik iade olur)
   • 12-24 saat cihaz ve IP'yi dinlendirin, farklı cihaz + farklı internet deneyin
   • VPN ile ülke eşleştirin (örn: ABD numara → ABD VPN)
   • Telefon uygulamasından giriş yapın (bilgisayar/web kullanmayın)
   • "Kaliteli" veya "Yüksek Kaliteli" etiketli numaraları tercih edin

🔹 **Ödeme/Bakiye Yansımadı:**
   • WhatsApp desteğine yönlendirme: **0543 726 59 86**
   • Ödeme bildirimi yaptıysanız 10-30 dakika bekleyin
   • Ödeme bilgilerini hazır bulundurun (tarih, saat, tutar, dekont)

🔹 **İade Talebi:**
   • Destek bilet sistemi üzerinden "Para İadesi" konulu talep oluşturun
   • SMS kodu alındıktan sonra kart/banka iadesi yapılamamaktadır
   • Kullanılmayan bakiye hesabınızda kalmaktadır

🔹 **Hesap/Numara Kapandı/Kısıtlandı:**
   • WhatsApp/Telegram geçici kısıtlaması olabilir, 12-24 saat bekleyin
   • Farklı cihaz ve farklı internet bağlantısı deneyin
   • VPN değiştirin (aynı ülke VPN kullanın)

🔹 **Stok Yok:**
   • Farklı ülke veya kategori deneyin
   • Premium ülkeler genellikle stokta bulunur

🔹 **Numara Tekrar Kullanım / 2FA:**
   • WhatsApp için: 2 aşamalı doğrulama (2FA) kurulumu yapın
   • 2FA ile numara kalıcı hale gelir ve sınırsız kullanabilirsiniz
   • Tek kullanımlık numaralar tekrar SMS alamaz

💡 **Size Daha İyi Yardımcı Olabilmem İçin Lütfen Şunları Paylaşın:**

• **Hangi servis?** (WhatsApp/Telegram/Google/Instagram/Bumble vs.)
• **Sorununuz nedir?** (SMS gelmiyor, ödeme yansımadı, iade talebi, hesap kapandı vb.)
• **Hangi ülke ve kategori?** ("Kaliteli" numara mı seçtiniz?)
• **Ekranda tam olarak ne yazıyor?** (Hata mesajı, bekleme süresi, doğrulama hatası vs.)
• **Ödeme yaptıysanız:** Ödeme yöntemi, tutar, tarih ve saat bilgisi

📱 **Hızlı Destek:**
• **Ödeme sorunları için:** WhatsApp: 0543 726 59 86
• **Diğer sorunlar için:** Destek bilet sistemi üzerinden talep oluşturun

İstersen ekranda yazan hatayı veya mesajı buraya kopyala, ona göre nokta atışı yönlendireyim! 🎯"""
        
        # Anlaşılamadı (BU SATIR ASLA ÇALIŞMAMALI)
        return "Merhaba. Sorununuzu daha detaylı açıklayabilir misiniz? Size en iyi şekilde yardımcı olabilmem için hangi konuda destek almak istiyorsunuz?\n\nEğer sorununuzla ilgili çözüm bulamıyorsanız, destek bilet sistemi üzerinden yeni bir talep oluşturabilirsiniz. Destek ekibimiz size yardımcı olacaktır."
    
    # ========== 6️⃣ KATEGORİ BAZLI CEVAPLAR ==========
    
    def _response_sms_gelmiyor(self, problem_source: str) -> str:
        """SMS gelmiyor sorunu için detaylı cevap - System Prompt Playbook"""
        response = "Merhaba. Kod gelmiyor yaşıyorsunuz; bunu genelde cihaz/IP kısıtı, yanlış akış veya yoğunluk tetikler.\n\n"
        response += "📋 **Çözüm Adımları (en olasıdan en az olasıya):**\n\n"
        response += "1️⃣ **Bekleme süresi (ÖNEMLİ):** Uygulama '23-24 saat sonra tekrar deneyin' diyorsa, bu WhatsApp/Telegram'ın geçici kısıtıdır. Belirtilen süreyi tamamen bekleyin (23-24 saat), daha erken deneme yapmayın (bekleme süresi uzar).\n\n"
        response += "⚠️ **Bekleme Süresi Kuralları:**\n"
        response += "• Bekleme süresi dolmadan tekrar deneme yaparsanız, bekleme süresi uzar\n"
        response += "• Bu süre zarfında başka numara denememelisiniz (aynı cihaz/IP üzerinden)\n"
        response += "• Bekleme süresi sonrası farklı cihaz + farklı internet deneyin\n\n"
        response += "2️⃣ **Numaralarım/Satın aldıklarım ekranını yenileyin:** 10-15 saniye aralıklarla yenileyin\n"
        response += "3️⃣ **Aynı numarada ısrar etmeyin:** Kod gelmiyorsa iptal → başka numara deneyin (iptalde bakiye otomatik iade olur)\n"
        response += "4️⃣ **Cihaz/IP kısıtı olasılığı:** 12-24 saat dinlendirin, farklı cihaz + farklı internet deneyin\n"
        response += "5️⃣ **VPN ile ülke eşleştirin:** Satın aldığınız ülke ile aynı ülke VPN kullanın (örn: ABD numara → ABD VPN)\n"
        response += "6️⃣ **Telefon uygulamasından giriş:** Sadece telefon uygulamasından kayıt olun (bilgisayar/web kullanmayın)\n"
        response += "7️⃣ **Kaliteli numara seçin:** \"Kaliteli\" veya \"Yüksek Kaliteli\" etiketli numaraları tercih edin\n"
        response += "8️⃣ **WhatsApp için:** WhatsApp 1 kategorisini kullanın\n"
        response += "9️⃣ **Telegram için:** ABD, Kanada, İngiltere ülkelerini deneyin\n\n"
        response += "💡 **Gerekli Bilgiler (Lütfen paylaşın):**\n\n"
        response += "• Hangi servis? (WhatsApp/Telegram/Google/Instagram/Bumble vs.)\n"
        response += "• Hangi ülke ve \"Kaliteli/Yüksek Kaliteli\" mi seçtiniz?\n"
        response += "• SMS ekranında tam olarak ne yazıyor? (güvenlik uyarısı, bekleme süresi, doğrulama hatası vs.)\n\n"
        response += "⚠️ **Önemli:** Numara iptal edilince bakiye otomatik iade olmaktadır.\n\n"
        response += "İstersen ekran yazısını buraya kopyala, ona göre nokta atışı yönlendireyim."
        return response
    
    def _response_whatsapp_dogrulama(self, problem_source: str) -> str:
        """WhatsApp doğrulama sorunu için cevap - System Prompt Playbook"""
        response = "Merhaba. WhatsApp doğrulama sorununuz; genelde güvenlik kısıtı, çok sık deneme veya cihaz/IP kısıtından kaynaklanır.\n\n"
        response += "📋 **Çözüm Adımları:**\n\n"
        response += "1️⃣ **Sadece telefondan kayıt:** WhatsApp doğrulamasını sadece telefon uygulamasından yapın (emülatör/PC web ile değil)\n"
        response += "2️⃣ **Bekleme süresi:** Çok fazla deneme yaptıysanız WhatsApp bekleme/limit koyabilir → 12-24 saat ara verin + tekrar deneyin\n"
        response += "3️⃣ **Bağlantı değiştirin:** Wi-Fi ↔ mobil veri değiştirin, uçak modu aç/kapat, cihazı yeniden başlatın\n"
        response += "4️⃣ **WhatsApp 1 kategorisi:** WhatsApp 1 kategorisindeki ülkeleri kullanın\n"
        response += "5️⃣ **Kaliteli numara:** \"Kaliteli\" veya \"Yüksek Kaliteli\" etiketli numaraları seçin\n"
        response += "6️⃣ **VPN ile ülke eşleştirin:** Satın aldığınız ülke ile aynı ülke VPN kullanın\n"
        response += "7️⃣ **Spam riskini düşürün:** Hesap açılır açılmaz yoğun mesaj/ekleme yapmayın; ilk birkaç saat düşük aktivite\n\n"
        if problem_source == 'cihaz_bani':
            response += "⚠️ **Güvenlik engeli:** Ekranda 'güvenliğiniz nedeniyle' benzeri uyarı çıkıyorsa bu WhatsApp'ın geçici kısıtı olabilir. 12-24 saat ara verip daha az denemeyle tekrar deneyin; mümkünse farklı internet + farklı cihaz kullanın.\n\n"
        response += "💡 **Gerekli Bilgiler:**\n\n"
        response += "• Hangi ülkeden numara aldınız?\n"
        response += "• WhatsApp doğrulamasında tam yazan metni buraya kopyalar mısınız?\n\n"
        response += "İstersen ekran yazısını buraya kopyala, ona göre nokta atışı yönlendireyim."
        return response
    
    def _response_telegram_dogrulama(self, problem_source: str) -> str:
        """Telegram doğrulama sorunu için cevap - System Prompt Playbook"""
        response = "Merhaba. Telegram kod sorununuz; bazen SMS yerine mevcut oturumun açık olduğu cihaza kod gönderilmesinden kaynaklanır.\n\n"
        response += "📋 **Çözüm Adımları:**\n\n"
        response += "1️⃣ **Eski cihaz kontrolü:** Eğer Telegram daha önce başka cihazda açıksa, o cihazda \"Telegram\" sistem mesajlarını kontrol edin\n"
        response += "2️⃣ **Uygulama temizliği:** Cihazda eski oturum/kalıntı varsa: Telegram uygulamasını kaldır-yükle, önbellek/uygulama verisini temizleyin\n"
        response += "3️⃣ **Kod gecikmesi:** OTP süresi dolmadan art arda istemeyin; 1-2 dakika bekleyin\n"
        response += "4️⃣ **Sadece telefon uygulamasından:** Telegram doğrulamasını sadece telefon uygulamasından yapın\n"
        response += "5️⃣ **Ülke seçimi:** ABD, Kanada, İngiltere ülkelerini kullanın (özellikle yüksek kaliteli/yoğun kullanılan)\n"
        response += "6️⃣ **Kaliteli numara:** \"Kaliteli\" veya \"Yüksek Kaliteli\" etiketli numaraları seçin\n"
        response += "7️⃣ **VPN ile ülke eşleştirin:** Satın aldığınız ülke ile aynı ülke VPN kullanın\n\n"
        response += "💡 **Telegram \"diğer cihaza gönderdik\" mesajı:** Telegram bazen SMS yerine kodu, hesabınızın daha önce açık olduğu cihaza gönderir. Daha önce Telegram'ı başka bir telefonda/tablette kullandıysanız o cihazdaki Telegram sistem mesajlarını kontrol edin.\n\n"
        response += "💡 **Gerekli Bilgi:** Tam ekranda ne yazıyor? Lütfen paylaşın."
        return response
    
    def _response_cihaz_ip_ban(self) -> str:
        """Cihaz/IP ban sorunu için cevap"""
        return "Merhaba. WhatsApp cihazınıza veya IP adresinize geçici bir yasak uyguladığında bu hata ortaya çıkar.\n\nYapmanız gereken:\n\n1️⃣ Cihazınızı en az 12 saat dinlendirin\n2️⃣ VPN değiştirin\n3️⃣ Farklı cihaz + farklı internet deneyin\n\n⚠️ Tekrar deneme yapmadan önce beklemeden denerseniz ban süresi uzar."
    
    def _response_numara_alamiyorum(self) -> str:
        """Numara alamıyorum sorunu için cevap"""
        return "Merhaba. Numara alamıyorum sorununuz için:\n\n1️⃣ Farklı ülke seçin\n2️⃣ Kaliteli numara seçin (ucuz numaralarda stok sorunu olabilir)\n3️⃣ WhatsApp 1 kategorisi veya Telegram için ABD, Kanada, İngiltere deneyin\n4️⃣ Stok durumunu kontrol edin - bazı operatörlerde anlık stok olmayabilir\n\n⚠️ \"Stok Yok\" uyarısı alıyorsanız, diğer ülkeleri deneyin. Premium ülkelerde stok genelde bulunur."
    
    def _response_stok_yok(self) -> str:
        """Stok yok hatası için cevap - System Prompt Playbook"""
        response = "Merhaba. \"Stok Yok\" uyarısı = o operatörde anlık stok olmadığını belirtir.\n\n"
        response += "📋 **Çözüm Adımları:**\n\n"
        response += "1️⃣ **Farklı ülke seçin:** Alternatif ülke/operatör deneyin\n"
        response += "2️⃣ **Alternatif kategori:** Farklı kategori seçeneklerini deneyin\n"
        response += "3️⃣ **Premium ülkeler:** Premium/yoğun kullanılan ülkelerde stok genelde bulunur\n"
        response += "4️⃣ **Önerilen ülkeler:** WhatsApp 1 kategorisi veya Telegram için ABD, Kanada, İngiltere kullanın\n\n"
        response += "⚠️ **Not:** Ucuz numaralarda yoğun talepten dolayı stoklar bitebilir. Yoğun saatler dışında tekrar deneyebilirsiniz.\n\n"
        response += "💡 **Stok güncellemesi:** Belirli ülkeler için stok güncellemesi genelde gün içinde yapılır. Birkaç saat sonra tekrar deneyebilirsiniz."
        return response
    
    def _response_para_iadesi(self) -> str:
        """Para iadesi talebi için cevap"""
        return "Merhaba. Numara alımı sonrası hizmet başlamış sayıldığı için:\n\n❌ Kart/banka iadesi yapılamamaktadır\n✅ Kullanılmayan bakiye hesabınızda kalmaktadır\n✅ Dilerseniz farklı numara deneyebilirsiniz\n\n⚠️ Numara sağlayıcı ücret keser, bu nedenle kart iadesi mümkün değildir. Bu bilgi kullanıcı sözleşmemizde belirtilmektedir."
    
    def _response_bakiye_yukleme(self) -> str:
        """Bakiye yükleme sorunu için cevap - System Prompt Playbook"""
        response = "Merhaba. Ödeme çekildi ama hesaba geçmedi sorununuz; genelde ödeme bildirimi yapılmaması veya işlem gecikmesinden kaynaklanır.\n\n"
        response += "📋 **Çözüm Adımları:**\n\n"
        response += "1️⃣ **Ödeme bildirimi kontrolü:** Ödeme bildirimi yaptınız mı? (Bakiye sayfasından \"Ödeme Bildirimi\" butonuna tıklayın)\n"
        response += "2️⃣ **İşlem gecikmesi:** Bazen banka işlemleri 1-2 saat gecikebilir, lütfen bekleyin\n"
        response += "3️⃣ **Ödeme yöntemi kontrolü:** Hangi yöntemle ödeme yaptınız? (kart/iban/papara)\n\n"
        response += "💡 **Gerekli Bilgiler (Elle kontrol için):**\n\n"
        response += "• Ödeme yöntemi (kart/IBAN/Papara)\n"
        response += "• Ödeme tarihi ve saati\n"
        response += "• Gönderen isim/IBAN'tan gönderildiyse gönderen adı\n"
        response += "• İşlem tutarı\n"
        response += "• Dekont veya ekran görüntüsü (varsa)\n\n"
        response += "Bu bilgileri WhatsApp destek hattımıza (0543 726 59 86) paylaşabilirsiniz veya destek bilet sistemi üzerinden talep oluşturabilirsiniz.\n\n"
        response += "⚠️ **Not:** Ödeme bildirimi yapılmazsa bakiye otomatik eklenmez. Ödeme yaptıktan sonra mutlaka bildirim yapmayı unutmayın."
        return response
    
    def _response_odeme_bildirimi(self) -> str:
        """Ödeme bildirimi için cevap"""
        return "Merhaba. Ödeme bildirimi yapmak için:\n\n1️⃣ Bakiye sayfasından \"Ödeme Bildirimi\" butonuna tıklayın\n2️⃣ Ödeme bilgilerinizi girin:\n   - Ödeme tarihi ve saati\n   - Gönderen isim\n   - Dekont (varsa)\n\nElle kontrol edip bakiyenizi işleyeceğiz.\n\n⚠️ Ödeme yaptıktan sonra mutlaka bildirim yapmayı unutmayın."
    
    def _response_sms_kodu_gecersiz(self) -> str:
        """SMS kodu geçersiz sorunu için cevap"""
        return "Merhaba. SMS kodu geçersiz/süresi doldu sorunu için:\n\n1️⃣ Kod süresi dolmuş olabilir → Yeni numara alın\n2️⃣ Kod geldiği anda girilmeli\n3️⃣ Sayfa yenilenmeli\n4️⃣ Yanlış girilmiş olabilir → Kontrol edin\n\n⚠️ SMS kodu geldikten sonra platform sorumluluk kabul etmez. Kod zamanında girilmeli ve sayfa kapatılmamalıdır."
    
    def _response_hesap_askiya(self) -> str:
        """Hesap askıya alındı sorunu için cevap - System Prompt Playbook"""
        response = "Merhaba. Hesap/numara kapatılması sorununuz; genelde WhatsApp/Telegram güvenlik politikaları, spam davranışı veya çok sık denemeden kaynaklanır.\n\n"
        response += "📋 **Sorunun Nedeni:**\n\n"
        response += "Yeni açılan hesaplar çeşitli nedenlerle kapatılabilir:\n\n"
        response += "• Hesap açılır açılmaz yoğun mesaj/ekleme yapılması\n"
        response += "• WhatsApp Business kullanımı\n"
        response += "• Spam davranışı (çok fazla mesaj gönderme)\n"
        response += "• Mimlenmiş cihaz/IP'den giriş yapılması\n\n"
        response += "📋 **Çözüm Adımları:**\n\n"
        response += "1️⃣ **24 saat bekleme:** Hesap açtıktan 24 saat sonra ilk mesajınızı gönderin\n"
        response += "2️⃣ **WhatsApp Business kullanmayın:** Standart WhatsApp kullanın\n"
        response += "3️⃣ **Spam davranışından kaçının:** İlk birkaç saat düşük aktivite, çok fazla mesaj göndermeyin\n"
        response += "4️⃣ **Farklı cihaz/IP:** Mimlenmiş cihaz/IP'den giriş yapmayın; farklı cihaz + farklı internet deneyin\n"
        response += "5️⃣ **12-24 saat ara:** Çok fazla deneme yaptıysanız 12-24 saat ara verip tekrar deneyin\n\n"
        response += "⚠️ **ÖNEMLİ:** SMS kodu alındıktan ve numara aktif edildikten sonra kapatılan hesaplar için sorumluluk kabul edilmemektedir. Kod geldikten sonra uygulama kaynaklı kapanma/ban gibi durumlarda platform sorumluluk kabul etmez, ancak kullanıcıyı çözüme yönlendiririz (bekleme, farklı cihaz, VPN, farklı ülke vb.). Bu bilgiler kullanıcı sözleşmemizde belirtilmektedir.\n\n"
        response += "💡 **Uygulama içinden itiraz:** WhatsApp/Telegram içinden inceleme/itiraz seçeneğini deneyin.\n\n"
        response += "İstersen hangi uygulama (WhatsApp/Telegram) ve ekranda ne yazıyor paylaş, ona göre daha spesifik yönlendireyim."
        return response
    
    def _response_numara_tekrar(self) -> str:
        """Numara tekrar kullanım için cevap - System Prompt Playbook"""
        response = "Merhaba. WhatsApp numarası ve 2 aşamalı doğrulama (2FA) hakkında bilgilendirme:\n\n"
        response += "📋 **Numara Kullanımı:**\n\n"
        response += "✅ **2FA ile kalıcı kullanım:** Numarayı aktif ettikten sonra WhatsApp hesabınıza 2 aşamalı doğrulama (2FA) kurulumu sağlarsanız numaranız kalıcı hale gelir.\n\n"
        response += "📋 **2FA Kurulum Adımları:**\n\n"
        response += "1️⃣ Numara ile WhatsApp'a kayıt olun\n"
        response += "2️⃣ WhatsApp ayarlarına gidin\n"
        response += "3️⃣ \"Hesap\" → \"İki aşamalı doğrulama\" bölümüne gidin\n"
        response += "4️⃣ 2FA'yı aktif edin ve şifre belirleyin\n"
        response += "5️⃣ Numara kalıcı hale gelir (WhatsApp hesabınızla bağlantılı kalır)\n\n"
        response += "📋 **Önemli Bilgiler:**\n\n"
        response += "• 2FA kurulumu sonrası numara WhatsApp hesabınıza bağlı kalır\n"
        response += "• WhatsApp hesabınız açık olduğu sürece numarayı sınırsız kullanabilirsiniz\n"
        response += "• 2FA kurulumu yapmadan numara tek kullanımlıktır (tekrar SMS alamaz)\n"
        response += "• Sınırsız SMS için numara kiralamanız da alternatif bir seçenektir\n\n"
        response += "💡 **Not:** 2FA kurulumu WhatsApp'ın kendi güvenlik özelliğidir. Kurulumu WhatsApp uygulaması üzerinden yapmanız gerekmektedir.\n\n"
        response += "Başka bir sorunuz varsa yardımcı olabilirim."
        return response
    
    def _response_2fa_kurulumu(self) -> str:
        """2FA kurulumu için cevap - System Prompt Playbook"""
        response = "Merhaba. 2 aşamalı doğrulama (2FA) kurulumu hakkında bilgilendirme:\n\n"
        response += "📋 **2FA Nedir ve Ne İşe Yarar?**\n\n"
        response += "2 aşamalı doğrulama (2FA), WhatsApp hesabınızı güvence altına alır ve numaranızı kalıcı hale getirir.\n\n"
        response += "📋 **Kurulum Adımları:**\n\n"
        response += "1️⃣ Numara ile WhatsApp'a kayıt olun\n"
        response += "2️⃣ WhatsApp ayarlarına gidin (⚙️)\n"
        response += "3️⃣ \"Hesap\" → \"İki aşamalı doğrulama\" bölümüne gidin\n"
        response += "4️⃣ 2FA'yı aktif edin ve 6 haneli bir şifre belirleyin\n"
        response += "5️⃣ E-posta adresinizi ekleyin (opsiyonel ama önerilir)\n"
        response += "6️⃣ Numara kalıcı hale gelir (WhatsApp hesabınızla bağlantılı kalır)\n\n"
        response += "📋 **2FA Avantajları:**\n\n"
        response += "✅ Numara kalıcı hale gelir\n"
        response += "✅ WhatsApp hesabınız ekstra güvenlik kazanır\n"
        response += "✅ Hesabınız açık olduğu sürece numarayı sınırsız kullanabilirsiniz\n\n"
        response += "⚠️ **Önemli:**\n\n"
        response += "• 2FA kurulumu yapmadan numara tek kullanımlıktır (tekrar SMS alamaz)\n"
        response += "• 2FA kurulumu WhatsApp'ın kendi güvenlik özelliğidir, platformdan bağımsızdır\n"
        response += "• Sınırsız SMS için alternatif olarak numara kiralamanız da mümkündür\n\n"
        response += "Başka bir sorunuz varsa yardımcı olabilirim."
        return response
    
    def _response_vpn_ulke_uyumsuz(self) -> str:
        """VPN/ülke uyumsuzluğu için cevap"""
        return "Merhaba. VPN/ülke uyumsuzluğu sorunu için:\n\n1️⃣ Seçtiğiniz ülkenin VPN'sini kullanın\n2️⃣ Örnek: ABD numarası → ABD VPN\n3️⃣ VPN ile ülke eşleştirirseniz uygulamalar SMS göndermeye daha meyilli olur\n\n⚠️ VPN kullanmadan SMS alma işlemi zorlaşabilir."
    
    def _response_sistem_hatasi(self) -> str:
        """Sistem hatası iddiası için cevap"""
        return "Merhaba. Sistem hatası iddianız için:\n\nEğer smspark.net'i ilgilendiren bariz bir hata varsa, bu tüm işlemleri içeren bir ekran videosu ile kanıtlanmalıdır.\n\nLütfen:\n1️⃣ Ekran görüntüsü veya video alın\n2️⃣ Hızlıresim.com'a yükleyin\n3️⃣ Linkini paylaşın\n\n⚠️ SMS kodu geldikten sonra platform sorumluluk kabul etmez."
    
    # ========== 7️⃣ ŞABLON YÜKLEME (Mevcut sistemden) ==========
    
    def _load_templates(self) -> Dict[str, List[str]]:
        """Cevap şablonlarını yükler"""
        try:
            with open('cevaplar.txt', 'r', encoding='utf-8') as f:
                content = f.read()
            
            templates_raw = [t.strip() for t in content.split('\n\n') if t.strip()]
            
            templates = {
                'sms_gelmiyor': [],
                'hesap_askiya': [],
                'bakiye': [],
                'numara': [],
                'stok': [],
                'genel': []
            }
            
            for template in templates_raw:
                template_lower = template.lower()
                if 'sms' in template_lower and ('gelmiyor' in template_lower or 'alamıyor' in template_lower):
                    templates['sms_gelmiyor'].append(template)
                elif 'hesap' in template_lower and ('kapandı' in template_lower or 'kapatılan' in template_lower):
                    templates['hesap_askiya'].append(template)
                elif 'bakiye' in template_lower or 'para' in template_lower:
                    templates['bakiye'].append(template)
                elif 'numara' in template_lower:
                    templates['numara'].append(template)
                elif 'stok' in template_lower:
                    templates['stok'].append(template)
                else:
                    templates['genel'].append(template)
            
            return templates
        except FileNotFoundError:
            return {}
    
    def _extract_keywords(self) -> Dict[str, List[str]]:
        """Anahtar kelimeleri çıkarır"""
        return {}  # Gelişmiş sistemde kullanılmıyor
    
    def _load_problem_patterns(self) -> Dict[str, Dict]:
        """Sorun kalıplarını yükler"""
        return {}  # Gelişmiş sistemde kullanılmıyor


# ========== 8️⃣ WEB ARAYÜZÜ İÇİN UYUMLULUK ==========

def main():
    """Ana fonksiyon"""
    chatbot = AdvancedSupportChatbot()
    
    print("=" * 60)
    print("GELİŞMİŞ SMSPARK DESTEK CHATBOTU")
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
        
        response = chatbot.generate_advanced_response(user_input)
        print(f"\nDestek: {response}\n")


if __name__ == '__main__':
    main()

