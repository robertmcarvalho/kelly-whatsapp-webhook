# API de Atendimento WhatsApp com UltraMsg + Together AI

## Como rodar localmente

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Variáveis de ambiente (.env)

- ULTRAMSG_INSTANCE_ID=...
- ULTRAMSG_TOKEN=...
- TOGETHER_API_KEY=...

## Rota principal

- `GET /` => Testa se a API está ativa
- `POST /webhook` => Recebe mensagens do WhatsApp via UltraMsg e responde com IA