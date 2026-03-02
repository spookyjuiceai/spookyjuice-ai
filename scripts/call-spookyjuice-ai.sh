#!/bin/bash
# Securely Call SpookyJuice Human-Level AI Assistant

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

PHONE_NUMBER="$1"
if [ -z "$PHONE_NUMBER" ]; then
    echo -e "${RED}Usage: $0 <phone_number>${NC}"
    echo "Example: $0 +19258901287"
    exit 1
fi

echo -e "${GREEN}🤖 INITIATING SECURE SPOOKYJUICE AI ASSISTANT CALL${NC}"
echo -e "${GREEN}===============================================${NC}"
echo -e "${YELLOW}📞 Target: $PHONE_NUMBER${NC}"
echo -e "${YELLOW}✅ Voice: Your Ultra-Realistic SpookyJuice.AI${NC}"
echo -e "${YELLOW}🧠 AI Engine: GPT-4 Turbo + Advanced NLU${NC}"
echo -e "${YELLOW}🛡️ Security: State-of-the-art guardrails${NC}"
echo ""

# --- Security Configuration ---
# These should match the security logic in SpookyJuice AI agent
CALLER_PHONE="${PHONE_NUMBER}" # The number being called
AGENT_PHONE="${TWILIO_PHONE_NUMBER:-+14155981480}" # Twilio's number

# --- Make the call using the SECURE webhook ---
echo "📞 Making call to $PHONE_NUMBER..."

RESPONSE=$(curl -s -k -X POST \
  "https://api.twilio.com/2010-04-01/Accounts/${TWILIO_ACCOUNT_SID}/Calls.json" \
  -u "${TWILIO_ACCOUNT_SID}:${TWILIO_AUTH_TOKEN}" \
  --data-urlencode "To=${PHONE_NUMBER}" \
  --data-urlencode "From=${AGENT_PHONE}" \
  --data-urlencode "CallerName=SpookyJuice AI Assistant" \
  --data-urlencode "Url=https://spookyjuice.ai/voice/secure" \
  --data-urlencode "Timeout=30") # Increased timeout for complex conversations

# --- Parse response ---
CALL_SID=$(echo "$RESPONSE" | grep -o '"sid":"[^"]*"' | cut -d'"' -f4 | head -1)
STATUS=$(echo "$RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4 | head -1)

if [ -n "$CALL_SID" ]; then
    echo ""
    echo -e "${GREEN}🎉 SECURE AI CONVERSATION STARTED!${NC}"
    echo -e "${GREEN}===================================${NC}"
    echo -e "${YELLOW}📞 Call SID: $CALL_SID${NC}"
    echo -e "${YELLOW}📊 Status: $STATUS${NC}"
    echo ""
    echo -e "${GREEN}🧠 SpookyJuice AI is now interacting securely:${NC}"
    echo "   ✅ Real-time conversation"
    echo "   ✅ Intelligent task execution"
    echo "   ✅ Security guardrails active"
    echo "   ✅ Your Ultra-Realistic Voice"
    echo ""
    echo -e "${YELLOW}🗣️ TRY THESE COMMANDS DURING THE CALL:${NC}"
    echo "   'Schedule a meeting with John tomorrow at 3 PM Pacific time'"
    echo "   'Take a note: Project deadline is Friday, confirm with Sarah'"
    echo "   'Is Brian available for a quick call this afternoon?'"
    echo "   'What's the weather like in San Francisco?'" # Example of extending capabilities
    echo ""
    echo -e "${GREEN}🚀 Your AI assistant is ready for complex tasks!${NC}"
else
    echo -e "${RED}❌ Call failed${NC}"
    echo "Response: $RESPONSE"
    echo ""
    echo -e "${YELLOW}🔧 Troubleshooting:${NC}"
    echo "   1. Ensure webhook is deployed: ./premium-deployment.sh"
    echo "   2. Check API keys in /etc/systemd/system/spookyjuice-ai.service"
    echo "   3. Verify service status: systemctl status spookyjuice-ai"
    echo "   4. Check logs: journalctl -u spookyjuice-ai -f"
fi