from fastapi import FastAPI, Request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

AGENTE_KELLY_API = os.getenv("AGENTE_KELLY_API", "https://web-production-xxxxxx.up.railway.app/mensagem")
ZAPI_URL = os.getenv("ZAPI_URL", "https://zapi.provedor.com/send-message")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN", "SEU_TOKEN_AQUI")

@app.post("/webhook")
async def receber_mensagem(request: Request):
    data = await request.json()
    numero = data.get("number")
    mensagem = data.get("message")

    if not numero or not mensagem:
        return {"erro": "Dados incompletos"}

    # Enviar mensagem para agente Kelly
    resposta = requests.post(
        AGENTE_KELLY_API,
        json={"mensagens": [{"role": "user", "content": mensagem}]},
        headers={"Content-Type": "application/json"}
    )

    if resposta.status_code != 200:
        return {"erro": "Falha ao consultar Kelly", "resposta": resposta.text}

    resposta_texto = resposta.json().get("resposta", "Não consegui entender. Pode repetir?")

    # Enviar resposta via Z-API (ou outro provedor)
import urllib.parse

# Formatando o número para padrão internacional
numero_formatado = numero if numero.startswith("+") else f"+55{numero}"

payload = {
    "token": os.getenv("ULTRAMSG_TOKEN"),
    "to": numero_formatado,
    "body": resposta_texto
}

url = f"https://api.ultramsg.com/{os.getenv('ULTRAMSG_INSTANCE_ID')}/messages/chat"

headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

envio = requests.post(url, data=urllib.parse.urlencode(payload), headers=headers)

    return {"status": "ok", "resposta_enviada": resposta_texto}
