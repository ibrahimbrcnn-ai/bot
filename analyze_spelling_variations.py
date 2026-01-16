#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ticket mesajlarından yazım hataları ve varyasyonları analiz eder
"""

import re
from collections import defaultdict, Counter

def extract_sql_inserts(filename):
    """SQL INSERT satırlarını çıkarır"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # INSERT INTO ... VALUES (...) formatı
    pattern = r"\((\d+),\s*'([^']*(?:''[^']*)*)',\s*(\d+),\s*(\d+),\s*(\d+)\)"
    matches = re.findall(pattern, content)
    
    rows = []
    for match in matches:
        # Tek tırnakları düzelt ('' -> ')
        message = match[1].replace("''", "'").replace("\\'", "'")
        rows.append((match[0], message, match[2], match[3], match[4]))
    
    return rows

def analyze_spelling_variations():
    """Yazım varyasyonlarını analiz eder"""
    print("Ticket mesajlarından yazım varyasyonları analiz ediliyor...\n")
    
    rows = extract_sql_inserts('ticket_messages.sql')
    
    # User 92 destek ekibi - sadece kullanıcı mesajlarını al
    user_messages = []
    for row in rows:
        id_val, message, ticket_id, user, time = row
        if int(user) != 92:  # Destek ekibi değilse
            user_messages.append(message.lower())
    
    print(f"Toplam {len(user_messages)} kullanıcı mesajı bulundu.\n")
    
    # Yaygın sorun kelimelerinin varyasyonlarını bul
    patterns = {
        'sms_gelmiyor': [
            r'sms\s+gelm\w*',
            r'kod\s+gelm\w*',
            r'sms\s+alam\w*',
            r'kod\s+alam\w*',
            r'onay.*gelm\w*',
            r'doğrulama.*gelm\w*'
        ],
        'numara_alamiyorum': [
            r'numara\s+alam\w*',
            r'numara\s+bulam\w*',
            r'numara\s+yok',
            r'numara.*istiyorum',
            r'numara.*bulunmuyor'
        ],
        'hesap_kapandi': [
            r'hesap.*kapand\w*',
            r'hesap.*kapat\w*',
            r'hesap.*kısıtland\w*',
            r'numara.*kapand\w*',
            r'numara.*kapat\w*',
            r'spam.*yed\w*',
            r'ban.*yed\w*'
        ]
    }
    
    variations = defaultdict(list)
    
    for category, pattern_list in patterns.items():
        print(f"\n=== {category.upper()} VARYASYONLARI ===")
        found_variations = set()
        
        for pattern in pattern_list:
            regex = re.compile(pattern, re.IGNORECASE)
            for msg in user_messages:
                matches = regex.findall(msg)
                for match in matches:
                    if match:
                        # Tam kelimeyi bul
                        words = msg.split()
                        for word in words:
                            if any(part in word for part in match.split()):
                                found_variations.add(word)
                                if msg not in variations[category]:
                                    variations[category].append(msg)
        
        # En yaygın varyasyonları göster
        print(f"Bulunan varyasyonlar (ilk 20):")
        for i, var in enumerate(sorted(found_variations)[:20], 1):
            print(f"  {i}. {var}")
        
        print(f"\nÖrnek mesajlar (ilk 5):")
        for i, msg in enumerate(variations[category][:5], 1):
            preview = msg[:80] + "..." if len(msg) > 80 else msg
            print(f"  {i}. {preview}")
    
    # Genel yazım hataları
    print("\n\n=== YAYGIN YAZIM HATALARI ===")
    common_mistakes = defaultdict(int)
    
    # "gelmiyor" varyasyonları
    gelmiyor_vars = []
    for msg in user_messages:
        if 'gelm' in msg or 'gelm' in msg:
            # "gelmiyor" benzeri kelimeleri bul
            words = re.findall(r'\b\w*gelm\w*\b', msg)
            gelmiyor_vars.extend(words)
    
    gelmiyor_counts = Counter(gelmiyor_vars)
    print("\n'gelmiyor' varyasyonları:")
    for word, count in gelmiyor_counts.most_common(15):
        if word not in ['gelmiyor', 'gelmedi', 'geliyor', 'gelmek']:
            print(f"  {word}: {count} kez")
    
    # "alamıyorum" varyasyonları
    alamıyorum_vars = []
    for msg in user_messages:
        if 'alam' in msg or 'alama' in msg:
            words = re.findall(r'\b\w*alam\w*\b', msg)
            alamıyorum_vars.extend(words)
    
    alamıyorum_counts = Counter(alamıyorum_vars)
    print("\n'alamıyorum' varyasyonları:")
    for word, count in alamıyorum_counts.most_common(15):
        if word not in ['alamıyorum', 'alamadım', 'alabilir', 'alamaz']:
            print(f"  {word}: {count} kez")
    
    # "kapandı" varyasyonları
    kapandı_vars = []
    for msg in user_messages:
        if 'kapan' in msg or 'kapat' in msg or 'kısıt' in msg:
            words = re.findall(r'\b\w*(?:kapan|kapat|kısıt)\w*\b', msg)
            kapandı_vars.extend(words)
    
    kapandı_counts = Counter(kapandı_vars)
    print("\n'kapandı/kısıtlandı' varyasyonları:")
    for word, count in kapandı_counts.most_common(15):
        print(f"  {word}: {count} kez")
    
    return variations, gelmiyor_counts, alamıyorum_counts, kapandı_counts

if __name__ == '__main__':
    analyze_spelling_variations()

