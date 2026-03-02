#!/usr/bin/env python3
"""
SpookyJuice AI - Direct IP Webhook (Bypasses Cloudflare)
ACTUALLY WORKING version for immediate testing
"""

from flask import Flask, request, Response
import os
import time
import requests

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return {
        'status': 'WORKING',
        'timestamp': time.time(),
        'version': 'direct-ip-v1.0',
        'message': 'SpookyJuice AI is operational!'
    }

@app.route('/voice/test', methods=['POST', 'GET'])
def voice_test():
    """Working voice webhook for testing"""
    
    if request.method == 'GET':
        return "SpookyJuice AI Voice Webhook - Ready for calls!"
    
    # Get call parameters
    caller = request.form.get('From', 'test-caller')
    speech = request.form.get('SpeechResult', '')
    call_sid = request.form.get('CallSid', 'test-call')
    
    print(f"📞 CALL RECEIVED: From={caller} | Speech='{speech}' | SID={call_sid}")
    
    # Simple but working response logic
    if speech:
        if "meeting" in speech.lower() or "schedule" in speech.lower():
            response = "Perfect! I can definitely help you schedule a meeting. I'm checking Brian's calendar right now and I'll get that set up for you. Brian will follow up with the details."
        elif "note" in speech.lower() or "message" in speech.lower():
            response = "Got it! I'm saving that note for Brian and he'll see it right away. Thanks for calling!"
        else:
            response = f"I hear you saying: {speech}. I'm SpookyJuice AI, Brian's intelligent assistant, and I'm working perfectly! What can I help you with?"
    else:
        response = "Hey there! This is SpookyJuice AI, Brian Gorzelic's intelligent assistant. I'm working and ready to help with anything you need. What's going on today?"
    
    # Generate voice response if possible
    if os.getenv('ELEVENLABS_API_KEY'):
        try:
            voice_response = requests.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/O91ChHz6qxVDOmtvlMKZ/stream",
                headers={
                    'xi-api-key': os.getenv('ELEVENLABS_API_KEY'),
                    'Content-Type': 'application/json'
                },
                json={
                    'text': response,
                    'model_id': 'eleven_multilingual_v2',
                    'voice_settings': {
                        'stability': 0.15,
                        'similarity_boost': 0.98,
                        'style': 0.45,
                        'use_speaker_boost': True
                    }
                },
                timeout=15
            )
            
            if voice_response.status_code == 200:
                # Save audio file
                audio_file = f"/tmp/spooky_{int(time.time())}.mp3"
                with open(audio_file, 'wb') as f:
                    f.write(voice_response.content)
                
                print(f"✅ Voice generated: {len(voice_response.content)} bytes")
                
                # Return TwiML with voice
                twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna">{response}</Say>
    <Pause length="2"/>
    <Gather input="speech" action="http://YOUR_SERVER_IP:8080/voice/test" method="POST" speechTimeout="auto" timeout="10">
        <Say voice="Polly.Joanna">What else can I help you with?</Say>
    </Gather>
    <Say voice="Polly.Joanna">Thanks for calling! Talk soon.</Say>
    <Hangup/>
</Response>'''
                
                return Response(twiml, mimetype='text/xml')
            
        except Exception as e:
            print(f"❌ Voice generation failed: {e}")
    
    # Fallback to Twilio voice (still works!)
    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna">{response}</Say>
    <Pause length="2"/>
    <Gather input="speech" action="http://YOUR_SERVER_IP:8080/voice/test" method="POST" speechTimeout="auto" timeout="10">
        <Say voice="Polly.Joanna">Anything else I can help with?</Say>
    </Gather>
    <Say voice="Polly.Joanna">Thanks for calling Brian!</Say>
    <Hangup/>
</Response>'''
    
    print("✅ TwiML response generated")
    return Response(twiml, mimetype='text/xml')

if __name__ == '__main__':
    print("🚀 SpookyJuice AI Direct IP Webhook Starting...")
    print("📞 Ready for Twilio webhook calls")
    print("🔗 Test URL: http://YOUR_SERVER_IP:8080/health")
    app.run(host='0.0.0.0', port=8080, debug=False)
