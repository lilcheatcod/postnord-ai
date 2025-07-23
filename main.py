from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/voice", methods=["POST"])
def voice():
    try:
        user_input = "The customer has called PostNord. Respond as a helpful AI assistant. Speak Swedish."

        client = openai.OpenAI()
        chat = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a friendly PostNord customer service AI that answers in Swedish."},
                {"role": "user", "content": user_input}
            ]
        )

        reply = chat.choices[0].message.content.strip()

        # Respond to the call with TwiML
        response = VoiceResponse()
        response.say(reply, language='sv-SE', voice='Polly.Astrid')  # You can change voice if needed
        return Response(str(response), mimetype='text/xml')

    except Exception as e:
        print(f"Error: {e}")
        return Response("<Response><Say>Internt fel uppstod. Försök igen senare.</Say></Response>", mimetype='text/xml')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
