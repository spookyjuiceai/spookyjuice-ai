#!/usr/bin/bash
# Secure Advanced SpookyJuice AI Agent Deployment
# Combines advanced conversation logic with robust security

echo "🚀 DEPLOYING SECURE ADVANCED SPOOKYJUICE AI AGENT"
echo "=============================================="

# --- Ensure prerequisite files are present ---
if [ ! -f "ultra-advanced-spookyjuice-ai.py" ] || [ ! -f "security_framework.py" ]; then
    echo "❌ ERROR: Missing required Python files."
    echo "Please ensure 'ultra-advanced-spookyjuice-ai.py' and 'security_framework.py' are in the current directory."
    exit 1
fi

# --- Install Python dependencies ---
echo "📦 Installing Python dependencies..."
pip3 install --upgrade \
    flask \
    gunicorn \
    requests \
    openai \
    google-auth \
    google-auth-oauthlib \
    google-api-python-client \
    asyncio \
    websockets \
    sqlite3 # Ensure sqlite3 is available or installed

# --- Prepare directories ---
echo "📂 Preparing directories..."
mkdir -p /var/log/spookyjuice-ai
mkdir -p /var/lib/spookyjuice-ai/memory # For conversation history
mkdir -p /var/lib/spookyjuice-ai/security # For security logs
mkdir -p /var/lib/spookyjuice-ai/notes # For task notes
mkdir -p /var/lib/spookyjuice-ai/meetings # For meeting logs
mkdir -p /tmp/voice_cache # For voice segments

# --- Copy agent and security framework ---
cp ultra-advanced-spookyjuice-ai.py /var/www/spookyjuice-ai/
cp security_framework.py /var/www/spookyjuice-ai/

# --- Configure Environment Variables ---
echo "🔧 Configuring environment variables..."

# Ensure these API keys are securely set in your environment or a .env file
# Example: export ELEVENLABS_API_KEY="your_professional_key"
# export OPENAI_API_KEY="sk-your-openai-key"
# export TWILIO_ACCOUNT_SID="ACxxxxxxx"
# export TWILIO_AUTH_TOKEN="your_twilio_token"

# Update the systemd service for the secured AI agent
cat > /etc/systemd/system/spookyjuice-ai.service << 'EOF'
[Unit]
Description=Secure SpookyJuice AI Advanced Agent
After=network.target google-users.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/spookyjuice-ai
Environment=ELEVENLABS_API_KEY=your_elevenlabs_professional_key
Environment=OPENAI_API_KEY=sk-your-openai-key
Environment=TWILIO_ACCOUNT_SID=ACxxxxxxx
Environment=TWILIO_AUTH_TOKEN=your_twilio_token
Environment=VOICE_WEBHOOK_BASE=https://spookyjuice.ai
ExecStart=/usr/local/bin/gunicorn --workers 4 --bind 0.0.0.0:5002 --timeout 120 --log-level info ultra-advanced-spookyjuice-ai:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# --- Nginx Configuration for Secure AI ---
# Ensure Nginx is set up to route traffic to the Flask app on port 5002
CAT > /etc/nginx/sites-available/spookyjuice-ai << 'EOF'
server {
    listen 443 ssl http2;
    server_name spookyjuice.ai;

    ssl_certificate /etc/ssl/certs/spookyjuice.ai.pem;
    ssl_certificate_key /etc/ssl/private/spookyjuice.ai.key;

    access_log /var/log/nginx/spookyjuice.ai.access.log;
    error_log /var/log/nginx/spookyjuice.ai.error.log;

    location /voice/ {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 10s;
        proxy_send_timeout 60s;
        proxy_read_timeout 120s;
        proxy_buffering off;
    }

    location /audio/cache/ {
        alias /tmp/voice_cache/;
        expires 1h;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# --- Enable and Start Services ---
echo "🚀 Starting SpookyJuice AI secured agent service..."
systemctl daemon-reload
systemctl enable spookyjuice-ai
systemctl restart spookyjuice-ai

echo "✅ Nginx configuration for /voice/* updated."
nginx -t && systemctl reload nginx

echo ""
echo "✅ SECURE ADVANCED SPOOKYJUICE AI AGENT DEPLOYED!"
echo "=================================================="
echo ""
echo "Features:"
echo "  - Ultra-Realistic Dynamic Conversations"
echo "  - Advanced NLU & Task Execution (GPT-4)"
echo "  - Your Custom SpookyJuice Voice (ElevenLabs Professional)"
echo "  - Robust Security: Auth, Injection Defense, Rate Limiting"
echo ""
echo "✅ ACTION REQUIRED: Update API keys in /etc/systemd/system/spookyjuice-ai.service!"
echo "   After updating, run: sudo systemctl daemon-reload && sudo systemctl restart spookyjuice-ai"
echo ""
echo "✅ To test: Run './call-spookyjuice-ai.sh +19258901287'"
echo "   (Make sure 'call-spookyjuice-ai.sh' is set up to use the /voice/secure endpoint)"