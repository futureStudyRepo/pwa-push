import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pywebpush import WebPushException, webpush

from .push_store import PushSubscriptionStore

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

app = FastAPI(title="PWA Push Demo")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
store = PushSubscriptionStore(DATA_DIR / "subscriptions.json")


def get_push_config() -> dict:
    return {
        "public_key": os.getenv("PWA_VAPID_PUBLIC_KEY", ""),
        "private_key": os.getenv("PWA_VAPID_PRIVATE_KEY", ""),
        "subject": os.getenv("PWA_VAPID_SUBJECT", "mailto:admin@example.com"),
    }


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "public_key": get_push_config()["public_key"],
        },
    )


@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    return templates.TemplateResponse(
        request,
        "admin.html",
        {
            "request": request,
            "subscription_count": len(store.all()),
        },
    )


@app.get("/api/config")
async def api_config():
    return get_push_config()


@app.post("/api/subscribe")
async def subscribe(request: Request):
    subscription = await request.json()
    if not subscription.get("endpoint"):
        raise HTTPException(status_code=400, detail="subscription endpoint is required")

    store.upsert(subscription)
    return {"message": "구독 정보가 저장되었습니다.", "count": len(store.all())}


@app.post("/api/send")
async def send_push(request: Request):
    payload = await request.json()
    config = get_push_config()

    if not config["public_key"] or not config["private_key"]:
        raise HTTPException(
            status_code=400,
            detail="VAPID 키가 설정되지 않았습니다. 환경변수를 먼저 설정해 주세요.",
        )

    message = {
        "title": payload.get("title", "관리자 메시지"),
        "body": payload.get("body", ""),
        "url": payload.get("url", "/"),
    }

    sent = 0
    failed = 0

    for subscription in store.all():
        try:
            webpush(
                subscription_info=subscription,
                data=json.dumps(message, ensure_ascii=False),
                vapid_private_key=config["private_key"],
                vapid_claims={"sub": config["subject"]},
            )
            sent += 1
        except WebPushException as exc:
            failed += 1
            status_code = getattr(getattr(exc, "response", None), "status_code", None)
            if status_code in (404, 410):
                store.remove_by_endpoint(subscription.get("endpoint", ""))

    return {
        "message": "푸시 발송을 시도했습니다.",
        "sent": sent,
        "failed": failed,
        "subscription_count": len(store.all()),
    }


@app.get("/api/subscriptions")
async def subscriptions():
    return JSONResponse(
        {
            "count": len(store.all()),
            "items": store.all(),
        }
    )
