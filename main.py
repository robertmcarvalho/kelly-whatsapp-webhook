from fastapi import FastAPI, Request
from pydantic import BaseModel
import os
import httpx
from dotenv import load_dotenv
import asyncio

load_dotenv()

app = FastAPI()

# Credenciais da UltraMsg via .env
ULTRAMSG_INSTANCE_ID = os.getenv("ULTRAMSG_INSTANCE_ID")
ULTRAMSG_TOKEN = os.getenv("ULTRAMSG_TOKEN")

# Prompt da agente Kelly
SYSTEM_PROMPT = """
Você é Kelly, agente de RH da cooperativa CoopMob. Sua missão é conversar com entregadores interessados em trabalhar como cooperados. 
Explique o funcionamento da cooperativa: sem vínculo empregatício, pagamentos semanais às quintas, cota de entrada de R$500, parcelável em até 25x com desconto em folha (segunda quinta do mês).
Explique também que é obrigatória a bag térmica (R$180 + frete, fornecida pela cooperativa se necessário) e o uniforme (camiseta R$47 + frete, sendo metade pago pela cooperativa e metade pelo cooperado, com desconto em folha também na segunda quinta do mês).
Depois, faça perguntas para triagem com base no perfil ideal:
- Idade entre 25 e 45
- Preferencialmente com filhos
- Escolaridade mínima: fundamental completo
- Mínimo de 6 meses de experiência com entregas
- Moto própria com CNH A válida
- Celular com Android (iOS desclassifica)
- Usa Google Maps e WhatsApp
- Boa apresentação e pontualidade
- Disponível para escala semanal
Avalie e classifique como Aprovado, Em Análise ou Reprovado.
"""

@app.post("/webhook")
async def receber_mensagem(request: Request):
    payload = await request.json()
    numero = payload.get("from")
    mensagem_usuario = payload.get("body")

    if not numero or not mensagem_usuario:
        return {"erro": "Dados ausentes"}

    resposta = await obter_resposta_da_kelly(mensagem_usuario)
    await enviar_resposta(numero, resposta)
    return {"status": "Mensagem processada com sucesso"}

async def obter_resposta_da_kelly(mensagem_usuario: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.together.xyz/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.getenv('TOGETHER_API_KEY')}"},
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": mensagem_usuario}
                ],
                "temperature": 0.4
            }
        )
        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "Erro ao gerar resposta.")

async def enviar_resposta(numero_destino: str, mensagem: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat",
            params={"token": ULTRAMSG_TOKEN},
            data={"to": numero_destino, "body": mensagem}
        )