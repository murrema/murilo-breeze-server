from flask import Flask, request, send_file
from openai import OpenAI
import os

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/')
def home():
    return "Servidor Breeze ativo e conectado à OpenAI!"

@app.route('/speak', methods=['GET', 'POST'])
def speak():
    # Pega o texto da URL ou usa o padrão se nenhum for enviado
    text = request.args.get("texto", "Olá, Murilo. A voz Breeze está funcionando perfeitamente!")
    
    speech_file_path = "voz_breeze.mp3"
    
    # Gera o áudio com a voz Breeze (pode mudar a voz depois)
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    ) as response:
        response.stream_to_file(speech_file_path)

    # Retorna o arquivo de áudio gerado
    return send_file(speech_file_path, mimetype="audio/mpeg")

if __name__ == '__main__':
    # Usa a porta do Railway automaticamente (ou 5000 localmente)
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
