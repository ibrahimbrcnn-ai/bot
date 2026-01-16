#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ticket mesajlarını analiz eder - kullanıcı soruları ve destek cevapları arasındaki ilişkiyi bulur
"""

import re
from collections import defaultdict

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
        rows.append(f"({match[0]}, '{message}', {match[2]}, {match[3]}, {match[4]})")
    
    return rows

def parse_message_row(row_str):
    """Message satırını parse eder"""
    # Basit parsing - SQL escape edilmiş string'ler için
    match = re.match(r"\((\d+),\s*'([^']*(?:''[^']*)*)',\s*(\d+),\s*(\d+),\s*(\d+)\)", row_str)
    if not match:
        return None
    
    id_val, message, ticket_id, user, time = match.groups()
    # Tek tırnakları düzelt
    message = message.replace("''", "'").replace("\\r\\n", "\n").replace("\\n", "\n")
    
    return {
        'id': int(id_val),
        'message': message,
        'ticket_id': int(ticket_id),
        'user': int(user),
        'time': int(time)
    }

def analyze_ticket_responses():
    """Ticket mesajlarını analiz eder - kullanıcı soruları ve cevapları eşleştirir"""
    print("Ticket mesajları analiz ediliyor...\n")
    
    rows = extract_sql_inserts('ticket_messages.sql')
    messages = []
    for row in rows:
        msg = parse_message_row(row)
        if msg:
            messages.append(msg)
    
    print(f"Toplam {len(messages)} mesaj bulundu.\n")
    
    # User 92 destek ekibi
    support_user_id = 92
    
    # Ticket'lara göre grupla
    tickets = defaultdict(list)
    for msg in messages:
        tickets[msg['ticket_id']].append(msg)
    
    # Her ticket için kullanıcı soruları ve destek cevaplarını eşleştir
    question_answer_pairs = []
    
    for ticket_id, msgs in sorted(tickets.items()):
        # Zaman sırasına göre sırala
        msgs.sort(key=lambda x: x['time'])
        
        user_questions = []
        for msg in msgs:
            if msg['user'] != support_user_id:
                # Kullanıcı mesajı
                user_questions.append({
                    'message': msg['message'],
                    'time': msg['time']
                })
            else:
                # Destek cevabı - önceki kullanıcı sorularına cevap
                if user_questions:
                    # Son kullanıcı sorusunu al
                    last_question = user_questions[-1]
                    question_answer_pairs.append({
                        'question': last_question['message'],
                        'answer': msg['message'],
                        'ticket_id': ticket_id
                    })
    
    print(f"Toplam {len(question_answer_pairs)} soru-cevap çifti bulundu.\n")
    
    # Kategorilere göre grupla
    categories = {
        'kapandı': [],
        'sms_gelmiyor': [],
        'bakiye': [],
        'numara': [],
        'stok': []
    }
    
    for pair in question_answer_pairs:
        q = pair['question'].lower()
        a = pair['answer'].lower()
        
        if any(word in q for word in ['kapandı', 'kapalı', 'kapatıldı', 'kapanıyor']):
            categories['kapandı'].append(pair)
        elif any(word in q for word in ['sms gelmiyor', 'kod gelmiyor', 'onay kodu', 'doğrulama gelmiyor']):
            categories['sms_gelmiyor'].append(pair)
        elif any(word in q for word in ['bakiye', 'para', 'ödeme', 'iade']):
            categories['bakiye'].append(pair)
        elif any(word in q for word in ['numara', 'numarası']):
            if 'kapandı' not in q and 'gelmiyor' not in q:
                categories['numara'].append(pair)
        elif any(word in q for word in ['stok', 'stokta yok', 'bulunamıyor']):
            categories['stok'].append(pair)
    
    # Her kategori için örnekler yazdır
    for category, pairs in categories.items():
        if pairs:
            print(f"\n=== {category.upper()} ({len(pairs)} örnek) ===")
            for i, pair in enumerate(pairs[:3], 1):  # İlk 3 örneği göster
                print(f"\n[Örnek {i}] Ticket {pair['ticket_id']}")
                print(f"Soru: {pair['question'][:100]}...")
                print(f"Cevap: {pair['answer'][:200]}...")
    
    # Anahtar kelime istatistikleri
    print("\n\n=== ANAHTAR KELİME İSTATİSTİKLERİ ===")
    keyword_counts = defaultdict(int)
    
    for pair in question_answer_pairs:
        q = pair['question'].lower()
        words = re.findall(r'\b\w+\b', q)
        for word in words:
            if len(word) > 3:  # 3'ten uzun kelimeler
                keyword_counts[word] += 1
    
    # En sık kullanılan kelimeler
    top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:30]
    print("\nEn sık kullanılan kelimeler:")
    for word, count in top_keywords:
        print(f"  {word}: {count}")
    
    return question_answer_pairs, categories

if __name__ == '__main__':
    analyze_ticket_responses()

