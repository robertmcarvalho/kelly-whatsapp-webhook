from fastapi import FastAPI, Request
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

ULTRAMSG_INSTANCE_ID = os.getenv("ULTRAMSG_INSTANCE_ID")
ULTRAMSG_TOKEN = os.getenv("ULTRAMSG_TOKEN")

# IA Kelly usando Together
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"

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

async def gerar_resposta_kelly(pergunta_usuario: str) -> str:
    async with httpx.AsyncClient() as client:
        resposta = await client.post(
            "https://api.together.xyz/v1/chat/completions",
            headers={"Authorization": f"Bearer {TOGETHER_API_KEY}"},
            json={
                "model": TOGETHER_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": pergunta_usuario}
                ],
                "temperature": 0.4
            }
        )
        resultado = resposta.json()
        return resultado["choices"][0]["message"]["content"]

@app.post("/webhook")
async def receber_whatsapp(request: Request):
    dados = await request.json()
    try:
        texto = dados["message"]
        numero = dados["from"]
        resposta_kelly = await gerar_resposta_kelly(texto)

        async with httpx.AsyncClient() as client:
            await client.get(
                f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat",
                params={
                    "token": ULTRAMSG_TOKEN,
                    "to": numero,
                    "body": resposta_kelly
                }
            )

        return {"status": "mensagem enviada", "para": numero, "resposta": resposta_kelly}
    except Exception as e:
        return {"erro": str(e), "payload_recebido": dados}