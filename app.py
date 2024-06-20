from flask import Flask

app = Flask(__name__)

# /ping - Verificar se está a funcionar
@app.route("/ping")
def ping():
    return "Pong!"