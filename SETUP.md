# SpookyJuice AI - Complete Setup Guide
## From Zero to Working AI Agent in 30 Minutes

## 🎯 WHAT THIS GETS YOU
- Ultra-realistic voice AI assistant
- Customer service and lead qualification
- Task execution (scheduling, notes, emails)
- Enterprise-grade security
- Production-ready deployment

## 🚀 QUICK START (30 minutes)

### Prerequisites
- Ubuntu server with 2GB+ RAM
- Domain name with SSL
- ElevenLabs Professional account
- OpenAI API access
- Twilio account

### Step 1: Clone Repository
```bash
git clone https://github.com/spookyjuiceai/spookyjuice-ai.git
cd spookyjuice-ai
```

### Step 2: Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Step 3: Deploy to Server
```bash
./scripts/deploy-production.sh
```

### Step 4: Test System
```bash
./scripts/test-working-system.sh YOUR_SERVER_IP
```

### Step 5: Configure Cloudflare (if needed)
```bash
python3 scripts/cloudflare-config.py
```

## 📞 TESTING YOUR DEPLOYMENT

### Outgoing Calls (SpookyJuice calls you)
```bash
./scripts/call-spookyjuice-ai.sh +1XXX-XXX-XXXX
```

### Incoming Calls (Customer service)
Call your Twilio number and test customer service AI

### Voice Quality Test
```bash
./scripts/voice-optimization.sh
```

## 🔧 TROUBLESHOOTING

### Common Issues
1. **Cloudflare 403**: Configure IP allowlist or use bypass
2. **Voice generation fails**: Check ElevenLabs API key
3. **AI not responding**: Verify OpenAI API access
4. **Service won't start**: Check logs with `journalctl -u spookyjuice-ai`

### Debug Commands
```bash
# Check system health
curl https://yourdomain.com/health

# View logs
tail -f /var/log/spookyjuice-ai/app.log

# Test voice generation
python3 tests/framework/cost-efficient-testing.py --level basic
```

## 📊 PERFORMANCE METRICS
- Voice generation: < 2 seconds
- AI processing: < 1 second  
- Total response time: < 3 seconds
- Cost per test: < $0.05

## 💰 COST OPTIMIZATION
- Use mock tests for development (FREE)
- Minimal real API tests for validation (~$0.05)
- Production testing only when needed (~$0.15)

---

**Built by SpookyJuice AI - Showcasing Enterprise AI Engineering**
