from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

ULTRAMSG_INSTANCE_ID = os.getenv("ULTRAMSG_INSTANCE_ID")
ULTRAMSG_TOKEN = os.getenv("ULTRAMSG_TOKEN")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

@app.get("/")
def root():
    return {"status": "ok", "message": "API ativa"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    message = data.get("body", {}).get("text", "")
    sender = data.get("body", {}).get("from", "")
    
    if not message or not sender:
        return {"status": "ignored"}

    # Gera resposta com a IA (mock básico)
    prompt = f"Responda como especialista em RH para o seguinte texto: {message}"
    ai_response = gerar_resposta_ia(prompt)

    # Envia resposta de volta ao WhatsApp via UltraMsg
    requests.post(
        f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat",
        data={
            "token": ULTRAMSG_TOKEN,
            "to": sender,
            "body": ai_response
        }
    )
    return {"status": "message_sent"}

def gerar_resposta_ia(prompt: str):
    response = requests.post(
        "https://api.together.xyz/inference",
        headers={
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "zero-one-ai/Yi-34B-Chat",
            "prompt": prompt,
            "max_tokens": 100,
            "temperature": 0.7
        }
    )
    if response.ok:
        return response.json().get("output", "Não foi possível gerar resposta.")
    return "Erro ao consultar a IA."