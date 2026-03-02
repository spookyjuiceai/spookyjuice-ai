#!/usr/bin/env python3
"""
MINIMAL WORKING SpookyJuice AI Webhook
Actually functional, no bullshit
"""

import os
import json
import time
from flask import Flask, request, Response
import requests

app = Flask(__name__)

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID', 'O91ChHz6qxVDOmtvlMKZ')

@app.route('/health', methods=['GET'])
def health():
    return {'status': 'working', 'timestamp': time.time()}

@app.route('/voice/test', methods=['POST'])
def test_webhook():
    """Minimal working webhook for testing"""
    
    caller = request.form.get('From', 'unknown')
    speech = request.form.get('SpeechResult', '')
    
    print(f"📞 INCOMING CALL: {caller} said: {speech}")
    
    # Simple response logic
    if speech:
        response = f"I heard you say: {speech}. This is SpookyJuice AI working!"
    else:
        response = "Hello! This is SpookyJuice AI. I'm working and ready to help!"
    
    # Generate voice (if API key available)
    if ELEVENLABS_API_KEY:
        try:
            voice_response = requests.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/stream",
                headers={'xi-api-key': ELEVENLABS_API_KEY, 'Content-Type': 'application/json'},
                json={'text': response, 'model_id': 'eleven_multilingual_v2'},
                timeout=10
            )
            
            if voice_response.status_code == 200:
                # Save for playback
                import hashlib
                audio_id = hashlib.md5(response.encode()).hexdigest()[:8]
                with open(f'/tmp/{audio_id}.mp3', 'wb') as f:
                    f.write(voice_response.content)
                
                twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>http://localhost:5001/audio/{audio_id}.mp3</Play>
    <Hangup/>
</Response>'''
                
                return Response(twiml, mimetype='text/xml')
                
        except Exception as e:
            print(f"Voice generation failed: {e}")
    
    # Fallback to Twilio voice
    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna">{response}</Say>
    <Hangup/>
</Response>'''
    
    return Response(twiml, mimetype='text/xml')

@app.route('/audio/<audio_id>.mp3', methods=['GET'])
def serve_audio(audio_id):
    """Serve generated audio files"""
    from flask import send_file
    try:
        return send_file(f'/tmp/{audio_id}.mp3', mimetype='audio/mpeg')
    except:
        return 'Audio not found', 404

if __name__ == '__main__':
    print("🔥 SpookyJuice AI Webhook STARTING")
    print(f"🎵 Voice ID: {ELEVENLABS_VOICE_ID}")
    app.run(host='0.0.0.0', port=5001, debug=False)
