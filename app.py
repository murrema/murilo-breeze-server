from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Rota principal
@app.route("/")
def index():
    return "Servidor Breeze ativo e pronto para uso!", 200

# Teste de vida
@app.route("/healthz")
def healthz():
    return "ok", 200

# Rota de fala (vai evoluir para usar voz Breeze)
@app.route("/speak", methods=["POST"])
def speak():
    data = request.get_json(force=True)
    text = data.get("text", "Olá Murilo, aqui é a voz Breeze.")
    return jsonify({
        "message": f"Breeze responderia: {text}"
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
