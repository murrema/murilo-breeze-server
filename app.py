from flask import Flask, request, send_file, jsonify
import openai
import os
from io import BytesIO

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def index():
    return "Servidor Breeze ativo e conectado à OpenAI!", 200

@app.route("/healthz")
def healthz():
    return "ok", 200

@app.route("/speak", methods=["POST"])
def speak():
    try:
        data = request.get_json(force=True)
        text = data.get("text", "Olá Murilo, aqui é a voz Breeze da OpenAI.")
        
        # Geração de voz Breeze
        response = openai.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="breeze",
            input=text
        )

        audio_data = BytesIO(response.read())
        return send_file(audio_data, mimetype="audio/mpeg")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
