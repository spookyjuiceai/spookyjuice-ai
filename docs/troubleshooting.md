# SpookyJuice AI - Troubleshooting Guide
## Solutions for Common Issues

## 🚨 IMMEDIATE FIXES

### Issue: Cloudflare 403 Errors
**Symptom**: Webhooks blocked, calls fail to connect
**Solution**: 
1. Add Twilio IPs to Cloudflare allowlist
2. Create page rule: `yourdomain.com/voice/*` → Security: Off
3. Or use bypass solution: `./scripts/cloudflare-bypass.sh`

### Issue: Voice Generation Fails
**Symptom**: Robotic voice or no voice response
**Solution**:
1. Check ElevenLabs API key: `curl -H "xi-api-key: YOUR_KEY" https://api.elevenlabs.io/v1/user`
2. Test voice generation: `./scripts/voice-optimization.sh`
3. Check voice ID: `O91ChHz6qxVDOmtvlMKZ`

### Issue: AI Not Responding Intelligently
**Symptom**: Generic responses, no task execution
**Solution**:
1. Check OpenAI API key and GPT-4 access
2. Test AI processing: `python3 tests/framework/cost-efficient-testing.py`
3. Check conversation context in logs

### Issue: Service Won't Start
**Symptom**: systemd service fails or webhook not accessible
**Solution**:
1. Check logs: `journalctl -u spookyjuice-ai -f`
2. Verify permissions: `chown -R www-data:www-data /var/www/spookyjuice-ai`
3. Test directly: `python3 /var/www/spookyjuice-ai/working_webhook.py`

## 📊 DEBUG COMMANDS

### Check System Health
```bash
curl https://yourdomain.com/health
curl https://yourdomain.com/debug/logs
```

### Monitor Real-Time
```bash
tail -f /var/log/spookyjuice-ai/app.log
journalctl -u spookyjuice-ai -f
```

### Test Components
```bash
# Test voice only
python3 scripts/voice-optimization.sh

# Test AI only  
python3 tests/framework/cost-efficient-testing.py --level mock_only

# Test full system
./scripts/test-working-system.sh YOUR_SERVER_IP
```

## 💰 COST MONITORING

### Track API Usage
```bash
grep "VOICE_SUCCESS\|AI_SUCCESS" /var/log/spookyjuice-ai/app.log | wc -l
```

### Estimate Costs
- Voice generation: ~$0.02 per minute
- AI conversation: ~$0.003 per interaction  
- Twilio calls: $0.013 per call

## 🎯 SHOWCASE READINESS CHECKLIST

### Before Demonstrating to Clients:
- [ ] Health check returns "healthy"
- [ ] Voice generation working (test with actual call)
- [ ] AI conversation responding intelligently
- [ ] Security system blocking injection attempts
- [ ] All logs showing successful operations
- [ ] Response times under 3 seconds
- [ ] No errors in recent logs

### Demo Script:
1. "Call this number and ask SpookyJuice to schedule a meeting"
2. Show voice quality and natural conversation
3. Demonstrate task execution (scheduling, notes)
4. Show security blocking bad actors
5. Display real-time logs and monitoring
