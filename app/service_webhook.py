from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from linebot import WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, AudioMessage, ImageMessage, FileMessage

from app.configs import Configs
from app import service_nlp, service_main, service_image
from app.user_state_store import get_user_state, has_user_state, clear_user_state

from app.file_utils import extract_text_from_file_message


router = APIRouter(tags=["Webhook"])
cfg = Configs()

parser = WebhookParser(cfg.LINE_CHANNEL_SECRET)


# ✅ แยกการจัดการข้อความตามประเภท
async def route_message_event(event):
    text = event.message.text.strip()
    user_id = getattr(event.source, "user_id", None)

    if text.startswith("#img"):
        await service_image.handle_event(event)

    elif user_id:
        state = get_user_state(user_id)
        if state:
            if state.startswith("image_") or state == "image_mode":
                await service_image.handle_event(event)
                return
            elif has_user_state(user_id):
                await service_nlp.handle_event(event)
                return

    if text.startswith("SELECT:"):
        await service_nlp.handle_event(event)
    elif text.startswith("#nlp"):
        await service_nlp.handle_event(event)
    else:
        await service_main.handle_event(event)


# ✅ Webhook main handler
@router.post("/aift")
async def webhook_handler(request: Request):
    signature = request.headers.get("X-Line-Signature")
    body = await request.body()

    try:
        events = parser.parse(body.decode("utf-8"), signature)
    except InvalidSignatureError as e:
        print("❌ Invalid signature:", e)
        return JSONResponse(content={"error": "Invalid signature"}, status_code=400)
    except Exception as e:
        print("❌ Failed to parse event:", e)
        return JSONResponse(content={"error": str(e)}, status_code=400)

    for event in events:
        try:
            if isinstance(event, MessageEvent):
                if isinstance(event.message, TextMessage):
                    await route_message_event(event)
                elif isinstance(event.message, AudioMessage): # AudioMessage Input
                    await service_nlp.handle_event(event)   # NLP service
                elif isinstance(event.message, ImageMessage): # ImageMessage Input
                    user_id = getattr(event.source, "user_id", None)
                    state = get_user_state(user_id) if user_id else None

                    if state and (state.startswith("image_") or state == "image_mode"):
                        await service_image.handle_event(event)
                    else:
                        await service_main.handle_event(event)
                elif isinstance(event.message, FileMessage): #Input file
                    try:
                        text_content = extract_text_from_file_message(event.message, event.message.id)
                        
                        # ✅ เรียกฟังก์ชันใหม่ที่เราสร้างไว้
                        await service_main.handle_text_from_file(event, text_content)

                    except Exception as e:
                        print("⚠️ Failed to process file:", e)
                        await service_main.send_message(event, "❌ ไม่สามารถประมวลผลไฟล์นี้ได้")

        except Exception as e:
            print("⚠️ Error handling event:", e)

    return JSONResponse(content={"message": "ok"}, status_code=200)



# @router.post("/aift")
# async def webhook_handler(request: Request):
#     signature = request.headers.get("X-Line-Signature")
#     body = await request.body()

#     try:
#         events = parser.parse(body.decode("utf-8"), signature)
#     except InvalidSignatureError as e:
#         print("❌ Invalid signature:", e)
#         return JSONResponse(content={"error": "Invalid signature"}, status_code=400)
#     except Exception as e:
#         print("❌ Failed to parse event:", e)
#         return JSONResponse(content={"error": str(e)}, status_code=400)

#     for event in events:
#         try:
#             if isinstance(event, MessageEvent):
#                 # ✅ ตรวจสอบข้อความ Text
#                 if isinstance(event.message, TextMessage):
#                     await route_message_event(event)

#                 # ✅ ตรวจสอบข้อความเสียง
#                 elif isinstance(event.message, AudioMessage):
#                     await service_nlp.handle_event(event)

#         except Exception as e:
#             print("⚠️ Error handling event:", e)

#     return JSONResponse(content={"message": "ok"}, status_code=200)

# 1.
# ✅ แยก Logic การจัดการข้อความให้เป็นระเบียบ
# async def route_message_event(event):
#     text = event.message.text.strip()
#     user_id = getattr(event.source, "user_id", None)

#     # print(f"📨 user_id: {user_id}, text: {text}")

#     # ✅ 1. จาก Rich Menu เช่น SELECT:tner
#     if text.startswith("SELECT:"):
#         await service_nlp.handle_event(event)

#     # ✅ 2. คำสั่ง NLP ที่ขึ้นต้นด้วย #nlp
#     elif text.startswith("#nlp"):
#         await service_nlp.handle_event(event)

#     # ✅ 3. ถ้ามี state รอจากผู้ใช้ไว้ก่อนหน้า
#     elif user_id and service_nlp.has_user_state(user_id):
#         await service_nlp.handle_event(event)

#     # ✅ 4. คำสั่ง image
#     elif text.startswith("#img"):
#         await service_image.handle_event(event)

#     # ✅ 5. อื่น ๆ
#     else:
#         await service_main.handle_event(event)

# 2.
# async def route_message_event(event):
#     text = event.message.text.strip()
#     user_id = getattr(event.source, "user_id", None)

#     # ✅ กรณีเริ่มใช้งาน image
#     if text.startswith("#img"):
#         await service_image.handle_event(event)
    
#     # ✅ เลือก image service (1–5)
#     elif user_id and service_nlp.has_user_state(user_id):
#         state = get_user_state(user_id)
#         if state and state.startswith("image_") or state == "image_mode":
#             await service_image.handle_event(event)
#         else:
#             await service_nlp.handle_event(event)

#     # ✅ NLP commands
#     elif text.startswith("SELECT:"):
#         await service_nlp.handle_event(event)
#     elif text.startswith("#nlp"):
#         await service_nlp.handle_event(event)
    
#     # ✅ fallback: main
#     else:
#         await service_main.handle_event(event)

