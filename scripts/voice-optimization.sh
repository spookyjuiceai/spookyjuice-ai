#!/bin/bash
# Professional Voice Optimization for SpookyJuice AI
# Test different models and settings for maximum realism

echo "🎵 PROFESSIONAL VOICE OPTIMIZATION TEST"
echo "======================================="
echo "Voice ID: O91ChHz6qxVDOmtvlMKZ (SpookyJuice.AI)"
echo ""

# Test text for comparison
TEST_TEXT="Hey there! This is SpookyJuice AI, Brian's intelligent assistant. I'm here to help with whatever you need - scheduling meetings, taking notes, or answering questions about Brian's availability."

# Test 1: Eleven v3 (Most expressive)
echo "1️⃣ Testing Eleven v3 (Most Expressive)..."
curl -k -X POST "https://api.elevenlabs.io/v1/text-to-speech/O91ChHz6qxVDOmtvlMKZ/stream" \
  -H "Accept: audio/mpeg" \
  -H "xi-api-key: ${ELEVENLABS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"text\": \"$TEST_TEXT\",
    \"model_id\": \"eleven_v3\",
    \"voice_settings\": {
      \"stability\": 0.40,
      \"similarity_boost\": 0.95,
      \"style\": 0.30
    },
    \"output_format\": \"mp3_44100_128\"
  }" --output voice_test_v3.mp3 --write-out "V3 Generation time: %{time_total}s\n"

# Test 2: Eleven Multilingual v2 (Most life-like)
echo ""
echo "2️⃣ Testing Multilingual v2 (Most Life-like)..."
curl -k -X POST "https://api.elevenlabs.io/v1/text-to-speech/O91ChHz6qxVDOmtvlMKZ/stream" \
  -H "Accept: audio/mpeg" \
  -H "xi-api-key: ${ELEVENLABS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"text\": \"$TEST_TEXT\",
    \"model_id\": \"eleven_multilingual_v2\",
    \"voice_settings\": {
      \"stability\": 0.30,
      \"similarity_boost\": 0.90,
      \"style\": 0.25,
      \"use_speaker_boost\": true
    },
    \"output_format\": \"mp3_44100_128\"
  }" --output voice_test_multi_v2.mp3 --write-out "Multilingual v2 Generation time: %{time_total}s\n"

# Test 3: Flash v2.5 (Ultra low latency)  
echo ""
echo "3️⃣ Testing Flash v2.5 (Ultra Low Latency)..."
curl -k -X POST "https://api.elevenlabs.io/v1/text-to-speech/O91ChHz6qxVDOmtvlMKZ/stream" \
  -H "Accept: audio/mpeg" \
  -H "xi-api-key: ${ELEVENLABS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"text\": \"$TEST_TEXT\",
    \"model_id\": \"eleven_flash_v2_5\",
    \"voice_settings\": {
      \"stability\": 0.35,
      \"similarity_boost\": 0.85
    },
    \"optimize_streaming_latency\": 4,
    \"output_format\": \"mp3_44100_128\"
  }" --output voice_test_flash.mp3 --write-out "Flash v2.5 Generation time: %{time_total}s\n"

# Test 4: Optimized Professional Settings
echo ""
echo "4️⃣ Testing Optimized Professional Settings..."
curl -k -X POST "https://api.elevenlabs.io/v1/text-to-speech/O91ChHz6qxVDOmtvlMKZ/stream" \
  -H "Accept: audio/mpeg" \
  -H "xi-api-key: ${ELEVENLABS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"text\": \"$TEST_TEXT\",
    \"model_id\": \"eleven_multilingual_v2\",
    \"voice_settings\": {
      \"stability\": 0.20,
      \"similarity_boost\": 0.95,
      \"style\": 0.40,
      \"use_speaker_boost\": true
    },
    \"output_format\": \"mp3_44100_192\",
    \"apply_text_normalization\": \"auto\"
  }" --output voice_test_optimized.mp3 --write-out "Optimized Generation time: %{time_total}s\n"

echo ""
echo "🎯 VOICE TEST RESULTS:"
echo "======================"
echo "✅ Generated 4 voice samples with different models"
echo ""
echo "📁 Audio Files Generated:"
echo "   voice_test_v3.mp3         (Most expressive)"
echo "   voice_test_multi_v2.mp3   (Most life-like)" 
echo "   voice_test_flash.mp3      (Ultra fast)"
echo "   voice_test_optimized.mp3  (Best settings)"
echo ""
echo "🎧 Listen to each and tell me which sounds most believable!"
echo "   The winner will become your new voice profile."