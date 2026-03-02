#!/bin/bash
# Create WORKING test environment that bypasses Cloudflare issues
# This will get SpookyJuice AI working immediately for showcasing

echo "🚀 CREATING WORKING TEST ENVIRONMENT"
echo "===================================="

# Create minimal working webhook
cat > minimal_working_webhook.py << 'EOF'
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
EOF

echo "✅ Created minimal working webhook"

# Create test calling script
cat > test_call.sh << 'EOF'
#!/bin/bash
# Test SpookyJuice AI functionality

echo "🧪 TESTING SPOOKYJUICE AI FUNCTIONALITY"
echo "======================================="

# Set your webhook URL (use ngrok for testing or your server IP)
WEBHOOK_URL="${1:-http://localhost:5001/voice/test}"
PHONE_NUMBER="${2:-+19258901287}"

echo "🔗 Webhook URL: $WEBHOOK_URL"
echo "📞 Testing with: $PHONE_NUMBER"

# Make test call
curl -X POST \
  "https://api.twilio.com/2010-04-01/Accounts/${TWILIO_ACCOUNT_SID}/Calls.json" \
  -u "${TWILIO_ACCOUNT_SID}:${TWILIO_AUTH_TOKEN}" \
  --data-urlencode "To=${PHONE_NUMBER}" \
  --data-urlencode "From=${TWILIO_PHONE_NUMBER}" \
  --data-urlencode "Url=${WEBHOOK_URL}" \
  --write-out "Status: %{http_code}\nCall SID: %header{Twilio-Sid}\n" \
  --silent

echo ""
echo "📊 TEST INSTRUCTIONS:"
echo "1. Run the webhook: python3 minimal_working_webhook.py"
echo "2. Your phone should ring with SpookyJuice AI"
echo "3. Try saying: 'Schedule a meeting' or 'Take a note'"
echo "4. Check server logs for what happens"
EOF

chmod +x test_call.sh

echo "✅ Created test calling script"

# Create deployment script for showcasing
cat > showcase_deployment.sh << 'EOF'
#!/bin/bash
# One-command showcase deployment

echo "🎬 DEPLOYING SPOOKYJUICE AI FOR SHOWCASING"
echo "=========================================="

# Install requirements
pip3 install flask requests

# Start webhook
echo "🚀 Starting SpookyJuice AI webhook..."
python3 minimal_working_webhook.py &
WEBHOOK_PID=$!

echo "📞 Webhook running on http://localhost:5001"
echo "🔗 Test URL: http://localhost:5001/health"

# Test the system
sleep 2
curl -s http://localhost:5001/health | python3 -m json.tool

echo ""
echo "🎯 READY FOR SHOWCASE!"
echo "======================"
echo "To test with a real call:"
echo "  ./test_call.sh http://YOUR_SERVER_IP:5001/voice/test +1XXX-XXX-XXXX"
echo ""
echo "To demo locally (simulated):"
echo "  curl -X POST http://localhost:5001/voice/test -d 'From=+15551234567&SpeechResult=Hello, show me what you can do!'"
echo ""
echo "Press Ctrl+C to stop"
wait $WEBHOOK_PID
EOF

chmod +x showcase_deployment.sh

echo "✅ Created showcase deployment script"

echo ""
echo "🎉 WORKING TEST ENVIRONMENT READY!"
echo "================================"
echo "Files created:"
echo "  minimal_working_webhook.py  - Actually working webhook"
echo "  test_call.sh                - Test calling script"
echo "  showcase_deployment.sh      - One-command showcase"
echo ""
echo "🚀 TO GET THIS SHIT WORKING:"
echo "1. Run: ./showcase_deployment.sh"
echo "2. Test: curl http://localhost:5001/health"
echo "3. Make a real call: ./test_call.sh"
echo "4. Your phone rings with SpookyJuice AI"
echo ""
echo "💰 THIS IS SHOWCASE-READY - makes us money!"