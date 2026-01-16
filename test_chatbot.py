#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chatbot Test Scripti
Farklı sorun tiplerini test eder
"""

from chatbot import SupportChatbot

def test_chatbot():
    """Chatbot'u farklı sorunlarla test eder"""
    chatbot = SupportChatbot()
    
    test_cases = [
        "SMS gelmiyor",
        "Kod gelmedi",
        "Bakiye gelmedi",
        "Numara alamıyorum",
        "Stok yok",
        "Hesap kapandı",
        "Whatsapp numarası aldım",
        "Telegram için numara almak istiyorum",
        "Para yatırdım ama gelmedi",
        "Numara tek kullanımlık mı?"
    ]
    
    print("=" * 60)
    print("CHATBOT TEST SONUÇLARI")
    print("=" * 60)
    print()
    
    for i, test_message in enumerate(test_cases, 1):
        print(f"[TEST {i}] Kullanıcı: {test_message}")
        
        # Problem tipini belirle
        problem_type, confidence = chatbot.classify_problem(test_message)
        print(f"  >> Tespit edilen problem: {problem_type} (Guven: {confidence:.2f})")
        
        # Cevap üret
        response = chatbot.generate_response(test_message)
        print(f"  >> Cevap: {response[:100]}...")
        print()
    
    print("=" * 60)
    print("TEST TAMAMLANDI")
    print("=" * 60)

if __name__ == '__main__':
    test_chatbot()

