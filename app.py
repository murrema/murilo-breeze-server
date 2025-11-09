import os
import uuid
import time
from pathlib import Path
from flask import Flask, request, jsonify, send_file, abort
import requests

# ============ CONFIGURAÇÃO ============
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "coloque_sua_chave_aqui")
INTERNAL_TOKEN = os.environ.get("INTERNAL_TOKEN", "murilo123secure")
OUTPUT_DIR = Path("./audio_cache")
OUTPUT_DIR.mkdir(exist_ok=True)
MAX_SECONDS_KEEP = 300  # tempo máximo dos áudios em segundos (5 min)
ALLOWED_VOICES = {"breeze"}
# ======================================

app = Flask(__name__)

def call_openai_tts(text: str, voice: str = "breeze"):
    """
    Gera áudio usando o modelo de voz Breeze da OpenAI
    """
    url = "https://api.openai.com/v1/audio/speech"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    payload = {"model": "tts-1-hd", "voice": voice, "input": text}
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    if not response.ok:
        raise Exception(response.text)
    return response.content

def cleanup_old_files():
    now = time.time()
    for f in OUTPUT_DIR.iterdir():
        if now - f.stat().st_mtime > MAX_SECONDS_KEEP:
            try:
                f.unlink()
            except:
                pass

@app.route("/healthz", methods=["GET"])
def health():
    return "ok"

@app.route("/speak", methods=["POST"])
def speak():
    """
    POST /speak
    headers: Authorization: Bearer <INTERNAL_TOKEN>
    json: { "text": "Olá Murilo", "voice": "breeze" }
    Retorna: { "url": "https://teusite/audio/<id>.mp3" }
    """
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer ") or auth.split(" ")[1] != INTERNAL_TOKEN:
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json(force=True)
    if not data or "text" not in data:
        return jsonify({"error": "missing_text"}), 400

    text = data["text"].strip()[:4000]
    voice = data.get("voice", "breeze")
    if voice not in ALLOWED_VOICES:
        voice = "breeze"

    try:
        audio_bytes = call_openai_tts(text, voice)
    except Exception as e:
        return jsonify({"error": str(e)}), 502

    audio_id = str(uuid.uuid4())
    file_path = OUTPUT_DIR / f"{audio_id}.mp3"
    with open(file_path, "wb") as f:
        f.write(audio_bytes)

    cleanup_old_files()
    base = request.url_root.rstrip("/")
    audio_url = f"{base}/audio/{audio_id}.mp3"
    return jsonify({"url": audio_url})

@app.route("/audio/<audio_id>.mp3", methods=["GET"])
def serve_audio(audio_id):
    path = OUTPUT_DIR / f"{audio_id}.mp3"
    if not path.exists():
        abort(404)
    return send_file(path, mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
