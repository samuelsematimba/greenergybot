import os
from fastapi import FastAPI, Request, Response, HTTPException, Query

app = FastAPI()
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "")

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
async def receive(request: Request):
    data = await request.json()
    print(data, flush=True)
    return {"status": "received"}