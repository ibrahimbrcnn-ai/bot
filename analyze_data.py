#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Destek Ticket Verilerini Analiz Eden Script
Ticket başlıkları, mesajlar ve sorun tiplerini analiz eder
"""

import re
import json
from collections import Counter, defaultdict
from datetime import datetime

def extract_sql_inserts(filename):
    """SQL dosyasından INSERT statement'larını çıkarır"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # INSERT INTO statementlarını bul
    pattern = r"INSERT INTO `[^`]+`[^)]+\)\s*VALUES\s*([^;]+);"
    matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
    
    all_values = []
    for match in matches:
        # Her satırdaki değerleri parse et
        lines = match.strip().split('\n')
        for line in lines:
            line = line.strip().rstrip(',')
            if line.startswith('('):
                all_values.append(line)
    
    return all_values

def parse_ticket_row(row_str):
    """Ticket satırını parse eder: (id, 'name', user, status, time)"""
    # Basit parsing - SQL formatı
    match = re.match(r"\((\d+),\s*'([^']*(?:''[^']*)*)',\s*(\d+),\s*(-?\d+),\s*(\d+)\)", row_str)
    if match:
        id_val, name, user, status, time = match.groups()
        # Escape edilmiş tek tırnakları düzelt
        name = name.replace("''", "'")
        return {
            'id': int(id_val),
            'name': name,
            'user': int(user),
            'status': int(status),
            'time': int(time)
        }
    return None

def parse_message_row(row_str):
    """Message satırını parse eder: (id, 'message', ticket_id, user, time)"""
    # Daha karmaşık - mesaj içinde özel karakterler olabilir
    # İlk parantez ve id'yi bul
    match = re.match(r"\((\d+),\s*'", row_str)
    if not match:
        return None
    
    id_val = int(match.group(1))
    # İkinci parantezden sonrasını bul (mesaj metni)
    remaining = row_str[match.end():]
    
    # Mesajı tek tırnaklar arasından çıkar (escape edilmiş tırnakları dikkate alarak)
    message = ""
    i = 0
    escaped = False
    while i < len(remaining):
        char = remaining[i]
        if escaped:
            message += char
            escaped = False
        elif char == '\\':
            escaped = True
            message += char
        elif char == "'" and i + 1 < len(remaining) and remaining[i+1] == "'":
            # Escape edilmiş tek tırnak
            message += "'"
            i += 1
        elif char == "'" and remaining[i+1:i+3] == "',":
            # Mesajın sonu
            break
        else:
            message += char
        i += 1
    
    # Kalan kısmı parse et (ticket_id, user, time)
    remaining = remaining[i+3:]  # "', " geç
    match2 = re.match(r"(\d+),\s*(\d+),\s*(\d+)\)", remaining)
    if match2:
        ticket_id, user, time = map(int, match2.groups())
        return {
            'id': id_val,
            'message': message,
            'ticket_id': ticket_id,
            'user': user,
            'time': time
        }
    return None

def analyze_tickets():
    """Ticket verilerini analiz eder"""
    print("Ticket verileri analiz ediliyor...")
    
    rows = extract_sql_inserts('tickets.sql')
    tickets = []
    for row in rows:
        ticket = parse_ticket_row(row)
        if ticket:
            tickets.append(ticket)
    
    print(f"Toplam {len(tickets)} ticket bulundu.")
    
    # Başlık analizi
    titles = [t['name'].lower() for t in tickets]
    title_counter = Counter(titles)
    
    print("\n=== EN SIK KARŞILAŞILAN TICKET BAŞLIKLARI ===")
    for title, count in title_counter.most_common(20):
        print(f"{count:4d} kez: {title}")
    
    # Sorun kategorileri
    categories = {
        'sms_gelmiyor': ['sms gelmiyor', 'sms gelmedi', 'kod gelmiyor', 'kod gelmedi', 'onay kodu', 'sms kodu'],
        'bakiye': ['bakiye', 'para', 'ödeme', 'yatırma', 'yatırdım', 'havale', 'eft'],
        'hesap_sorunlari': ['hesap', 'kapandı', 'engellendi', 'spam', 'kısıt', 'ban'],
        'numara': ['numara', 'stok', 'geçersiz', 'iptal'],
        'telegram': ['telegram', 'tg'],
        'whatsapp': ['whatsapp', 'whatsap', 'wp'],
        'teknik': ['giriş', 'hata', 'sorun', 'çalışmıyor']
    }
    
    categorized = defaultdict(int)
    for ticket in tickets:
        title_lower = ticket['name'].lower()
        for category, keywords in categories.items():
            if any(kw in title_lower for kw in keywords):
                categorized[category] += 1
                break
    
    print("\n=== SORUN KATEGORİLERİ ===")
    for category, count in sorted(categorized.items(), key=lambda x: x[1], reverse=True):
        print(f"{category:20s}: {count:4d} ticket")
    
    return tickets, categorized

def analyze_messages():
    """Ticket mesajlarını analiz eder"""
    print("\nTicket mesajları analiz ediliyor...")
    
    rows = extract_sql_inserts('ticket_messages.sql')
    messages = []
    for row in rows:
        msg = parse_message_row(row)
        if msg:
            messages.append(msg)
    
    print(f"Toplam {len(messages)} mesaj bulundu.")
    
    # Kullanıcı mesajları vs destek mesajları
    # User 92 muhtemelen destek ekibi
    user_messages = [m for m in messages if m['user'] != 92]
    support_messages = [m for m in messages if m['user'] == 92]
    
    print(f"Kullanıcı mesajları: {len(user_messages)}")
    print(f"Destek mesajları: {len(support_messages)}")
    
    # En uzun destek mesajları (muhtemelen şablonlar)
    support_messages.sort(key=lambda x: len(x['message']), reverse=True)
    
    print("\n=== UZUN DESTEK MESAJLARI (ŞABLON ADAYLARI) ===")
    for i, msg in enumerate(support_messages[:10]):
        preview = msg['message'][:150].replace('\r\n', ' ').replace('\n', ' ')
        print(f"\n[{i+1}] Ticket {msg['ticket_id']} ({len(msg['message'])} karakter):")
        print(f"    {preview}...")
    
    return messages, support_messages, user_messages

def extract_response_templates():
    """cevaplar.txt dosyasındaki şablonları çıkarır"""
    print("\ncevaplar.txt dosyası analiz ediliyor...")
    
    with open('cevaplar.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Boş satırlarla ayrılmış cevaplar
    responses = [r.strip() for r in content.split('\n\n') if r.strip()]
    
    print(f"Toplam {len(responses)} cevap şablonu bulundu.")
    
    # Her şablonu kategorilere göre sınıflandır
    templates_by_category = defaultdict(list)
    
    for response in responses:
        response_lower = response.lower()
        if 'sms' in response_lower and ('gelmiyor' in response_lower or 'gelmedi' in response_lower):
            templates_by_category['sms_gelmiyor'].append(response)
        elif 'hesap' in response_lower and ('kapandı' in response_lower or 'kapatılan' in response_lower):
            templates_by_category['hesap_kapandı'].append(response)
        elif 'bakiye' in response_lower or 'para' in response_lower or 'iade' in response_lower:
            templates_by_category['bakiye'].append(response)
        elif 'stok' in response_lower:
            templates_by_category['stok'].append(response)
        elif 'numara' in response_lower and 'kalıcı' in response_lower:
            templates_by_category['numara_kalıcılık'].append(response)
        elif 'hata' in response_lower or 'geçici yasak' in response_lower:
            templates_by_category['hata'].append(response)
        else:
            templates_by_category['diğer'].append(response)
    
    print("\n=== CEVAP ŞABLONLARI KATEGORİLERE GÖRE ===")
    for category, templates in templates_by_category.items():
        print(f"\n{category}: {len(templates)} şablon")
    
    return responses, templates_by_category

def save_analysis_results(tickets, messages, responses, templates_by_category):
    """Analiz sonuçlarını JSON olarak kaydeder"""
    analysis = {
        'ticket_count': len(tickets),
        'message_count': len(messages),
        'response_template_count': len(responses),
        'templates_by_category': {k: len(v) for k, v in templates_by_category.items()},
        'top_problems': [],
        'common_keywords': []
    }
    
    # En sık karşılaşılan sorunlar
    title_counter = Counter([t['name'].lower() for t in tickets])
    analysis['top_problems'] = [{'problem': k, 'count': v} for k, v in title_counter.most_common(15)]
    
    # Anahtar kelimeler
    all_text = ' '.join([t['name'] for t in tickets]).lower()
    words = re.findall(r'\b\w{4,}\b', all_text)  # 4+ harfli kelimeler
    word_counter = Counter(words)
    analysis['common_keywords'] = [{'word': k, 'count': v} for k, v in word_counter.most_common(20)]
    
    with open('analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    print("\nAnaliz sonuçları 'analysis_results.json' dosyasına kaydedildi.")

if __name__ == '__main__':
    print("=" * 60)
    print("DESTEK TICKET VERİ ANALİZİ")
    print("=" * 60)
    
    tickets, categorized = analyze_tickets()
    messages, support_messages, user_messages = analyze_messages()
    responses, templates_by_category = extract_response_templates()
    
    save_analysis_results(tickets, messages, responses, templates_by_category)
    
    print("\n" + "=" * 60)
    print("ANALİZ TAMAMLANDI")
    print("=" * 60)

