from linebot import LineBotApi
from fastapi import APIRouter, Request
from linebot.models import TextSendMessage, MessageEvent, TextMessage
from datetime import datetime

from app.configs import Configs
from aift import setting
from aift.multimodal import textqa

cfg = Configs()
setting.set_api_key(cfg.AIFORTHAI_APIKEY)
line_bot_api = LineBotApi(cfg.LINE_CHANNEL_ACCESS_TOKEN)

router = APIRouter(tags=["Main"], prefix="/message")

# ✅ ฟังก์ชันหลักที่ถูกเรียกจาก service_webhook.py
async def handle_event(event: MessageEvent):
    if isinstance(event.message, TextMessage):
        user_text = event.message.text.strip()

        # สร้าง session_id จากวันเวลา (เช่น 17061520)
        now = datetime.now()
        session_id = f"{now.day:02}{now.month:02}{now.hour:02}{(now.minute // 10) * 10:02}"

        try:
            result = textqa.chat(
                user_text,
                session_id + cfg.AIFORTHAI_APIKEY,
                temperature=0.6,
                context=""
            )
            reply = result["response"]
        except Exception as e:
            reply = f"⚠️ ขออภัย, ระบบตอบกลับล้มเหลว: {str(e)}"

        send_message(event, reply)
    else:
        send_message(event, "❗️ไม่รองรับประเภทข้อความนี้ครับ")

# ✅ ฟังก์ชันส่งข้อความตอบกลับ
def send_message(event, message: str):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message)
    )
