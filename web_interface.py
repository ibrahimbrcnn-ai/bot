#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chatbot Web Arayüzü
Flask kullanarak basit web arayüzü
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from chatbot_advanced import AdvancedSupportChatbot
import json

app = Flask(__name__)
# CORS ayarları - smspark.net için izin ver
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://smspark.net", "http://smspark.net", "https://www.smspark.net", "http://www.smspark.net"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})
chatbot = AdvancedSupportChatbot()

@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')

@app.route('/widget')
def widget():
    """Chatbot widget sayfası (tüm sayfalara eklenebilir)"""
    return render_template('chatbot_widget.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat API endpoint"""
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'Mesaj boş olamaz'}), 400
    
    # Chatbot cevabını al (gelişmiş sistem)
    response = chatbot.generate_advanced_response(user_message)
    
    return jsonify({
        'response': response,
        'status': 'success'
    })

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'SMSPark Support Chatbot'})

if __name__ == '__main__':
    print("Chatbot web arayüzü başlatılıyor...")
    print("Tarayıcınızda http://localhost:5000 adresini açın")
    app.run(debug=True, host='0.0.0.0', port=5000)

