import os
import httpx
from fastapi import FastAPI, Request, Response, HTTPException, Query, BackgroundTasks

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "")
GRAPH_VERSION = os.getenv("GRAPH_VERSION", "v23.0")
GRAPH_URL = f"https://graph.facebook.com/{GRAPH_VERSION}/{PHONE_NUMBER_ID}/messages"


def send_text(to: str, text: str):
    r = httpx.post(
        GRAPH_URL,
        headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}"},
        json={
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text},
        },
        timeout=20,
    )
    print("send status:", r.status_code, r.text, flush=True)


def handle_message(sender: str, text: str):
    # For now: echo. Later this is where we call the assistant.
    send_text(sender, f"You said: {text}")


@app.get("/")
def home():
    return {"status": "ok"}


@app.get("/webhook")
def verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return Response(content=hub_challenge, media_type="text/plain")
    raise HTTPException(status_code=403)


@app.post("/webhook")
async def receive(request: Request, background: BackgroundTasks):
    data = await request.json()
    print(data, flush=True)
    try:
        value = data["entry"][0]["changes"][0]["value"]
        for msg in value.get("messages", []):
            if msg.get("type") == "text":
                background.add_task(handle_message, msg["from"], msg["text"]["body"])
    except (KeyError, IndexError):
        pass
    return {"status": "received"}   # answer Meta quickly, do the work in the background
