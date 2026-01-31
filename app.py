from flask import Flask, render_template, request, jsonify, send_file
from gtts import gTTS
import os
import tempfile
import uuid
from datetime import datetime
import json

app = Flask(__name__)

# مجلد مؤقت للملفات الصوتية
AUDIO_FOLDER = tempfile.gettempdir()

# قائمة الأصوات المتاحة (gTTS يدعم أصوات مختلفة عبر اللهجات)
VOICES = {
    'ar': {
        'standard': {'name': 'عربي قياسي', 'lang': 'ar', 'tld': 'com'},
        'egyptian': {'name': 'مصري', 'lang': 'ar', 'tld': 'com.eg'},
        'saudi': {'name': 'سعودي', 'lang': 'ar', 'tld': 'com.sa'},
        'moroccan': {'name': 'مغربي', 'lang': 'ar', 'tld': 'co.ma'},
        'gulf': {'name': 'خليجي', 'lang': 'ar', 'tld': 'ae'},
    },
    'en': {
        'us': {'name': 'American', 'lang': 'en', 'tld': 'com'},
        'uk': {'name': 'British', 'lang': 'en', 'tld': 'co.uk'},
        'aus': {'name': 'Australian', 'lang': 'en', 'tld': 'com.au'},
        'india': {'name': 'Indian', 'lang': 'en', 'tld': 'co.in'},
        'ireland': {'name': 'Irish', 'lang': 'en', 'tld': 'ie'},
        'canada': {'name': 'Canadian', 'lang': 'en', 'tld': 'ca'},
        'south_africa': {'name': 'South African', 'lang': 'en', 'tld': 'co.za'},
    }
}

# سرعات التشغيل
SPEEDS = {
    'very_slow': {'name': 'بطيء جداً', 'value': 0.5},
    'slow': {'name': 'بطيء', 'value': 0.75},
    'normal': {'name': 'عادي', 'value': 1.0},
    'fast': {'name': 'سريع', 'value': 1.25},
    'very_fast': {'name': 'سريع جداً', 'value': 1.5},
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/voices', methods=['GET'])
def get_voices():
    """إرجاع قائمة الأصوات المتاحة"""
    return jsonify({
        'voices': VOICES,
        'speeds': SPEEDS
    })

@app.route('/api/generate', methods=['POST'])
def generate_audio():
    """توليد الملف الصوتي"""
    try:
        data = request.json
        text = data.get('text', '')
        language = data.get('language', 'ar')
        voice_type = data.get('voice', 'standard')
        speed = data.get('speed', 'normal')
        
        if not text:
            return jsonify({'error': 'النص مطلوب'}), 400
        
        # الحصول على إعدادات الصوت
        voice_config = VOICES.get(language, {}).get(voice_type, VOICES['ar']['standard'])
        speed_value = SPEEDS.get(speed, SPEEDS['normal'])['value']
        
        # توليد اسم ملف فريد
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(AUDIO_FOLDER, filename)
        
        # توليد الصوت
        tts = gTTS(
            text=text,
            lang=voice_config['lang'],
            tld=voice_config['tld'],
            slow=(speed_value < 1.0)
        )
        tts.save(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'url': f'/api/audio/{filename}',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/audio/<filename>', methods=['GET'])
def get_audio(filename):
    """تحميل الملف الصوتي"""
    try:
        filepath = os.path.join(AUDIO_FOLDER, filename)
        if os.path.exists(filepath):
            return send_file(filepath, mimetype='audio/mpeg')
        return jsonify({'error': 'الملف غير موجود'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """الحصول على سجل التحويلات"""
    # يمكن تطوير هذا لحفظ السجل في قاعدة بيانات
    return jsonify({'history': []})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
