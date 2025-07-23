from flask import Flask, request, Response
import openai
import os
import requests
from twilio.twiml.voice_response import VoiceResponse
import re

app = Flask(__name__)

# Load API keys from environment
openai.api_key = os.environ.get("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID")

# ElevenLabs TTS settings
def speak(message: str) -> str:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/stream"
    headers = {
        "Accept": "audio/mpeg",
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": message,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.7,
            "style": 1,
            "use_speaker_boost": True
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    with open("response.mp3", "wb") as f:
        f.write(response.content)
    return "/response.mp3"

def clean_text(text):
    return re.sub(r"[^A-Za-z0-9ÅÄÖåäö\s,.!?-]", "", text)

@app.route("/voice", methods=["POST"])
def voice():
    user_input = request.form.get("SpeechResult", "")
    if not user_input:
        user_input = "Användaren sa inget."

    messages = [
        {"role": "system", "content": "Du är en emotionell och hjälpsam svensk kundtjänstrepresentant för PostNord. Hjälp kunden med deras frågor kring paketspårning, förseningar, tullproblem och ge tydliga instruktioner. Svara alltid med värme och empati."},
        {"role": "user", "content": user_input}
    ]

    chat = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.8,
        max_tokens=300
    )

    gpt_reply = clean_text(chat.choices[0].message.content.strip())
    audio_path = speak(f"ehh... {gpt_reply}")

    response = VoiceResponse()
    response.play(f"https://{request.host}{audio_path}")
    return Response(str(response), mimetype="application/xml")

@app.route("/response.mp3", methods=["GET"])
def serve_audio():
    with open("response.mp3", "rb") as f:
        return Response(f.read(), mimetype="audio/mpeg")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # required for Railway
    app.run(host="0.0.0.0", port=port)
