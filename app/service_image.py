from fastapi import APIRouter
from linebot import LineBotApi
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    ImageMessage, ImageSendMessage
)

import requests
from datetime import datetime

from aift import setting
from aift.image.detection import face_blur
from aift.image.classification import chest_classification, violence_classification, nsfw
from aift.image import super_resolution

from app.configs import Configs
from app.user_state_store import set_user_state, get_user_state, clear_user_state

router = APIRouter(tags=["Image"])
cfg = Configs()

setting.set_api_key(cfg.AIFORTHAI_APIKEY)
line_bot_api = LineBotApi(cfg.LINE_CHANNEL_ACCESS_TOKEN)

IMAGE_COMMANDS = {
    '1': 'face_blur',
    '2': 'chest_classification',
    '3': 'violence_classification',
    '4': 'nsfw',
    '5': 'super_resolution',
    '6': 'person detection',
    '7': 'caption generation'
}

# ✅ Main event handler
async def handle_event(event):
    if isinstance(event.message, TextMessage):
        await handle_text(event)
    elif isinstance(event.message, ImageMessage):
        await handle_image(event)

# ✅ Text handler (for #img and selecting 1–5)
async def handle_text(event):
    user_id = event.source.user_id
    user_input = event.message.text.strip()

    # Step 1: User enters #img
    if user_input == "#img":
        set_user_state(user_id, "image_mode")
        send_message(event, (
            "🖼️ กรุณาเลือกบริการประมวลผลภาพ:\n"
            "1. Face Blur\n"
            "2. Chest X-Ray\n"
            "3. Violence Detection\n"
            "4. NSFW Detection\n"
            "5. Super Resolution\n"
            "6. Person Detection\n"
            "7. Caption Generation"
        ))
        return

    # Step 2: User selects model 1-5
    current_state = get_user_state(user_id)

    if not current_state and user_input in IMAGE_COMMANDS:
        send_message(event, "⏱ หมดเวลา 3 นาทีแล้ว กรุณาพิมพ์ #img เพื่อเริ่มใหม่อีกครั้ง")
        return

    if current_state == "image_mode" and user_input in IMAGE_COMMANDS:
        set_user_state(user_id, f"image_{user_input}")
        send_message(event, f"✅ เลือกบริการ: {IMAGE_COMMANDS[user_input]} แล้ว กรุณาส่งภาพเข้ามา")
    else:
        send_message(event, "⚠️ กรุณาพิมพ์ #img เพื่อเริ่มใช้งานบริการวิเคราะห์ภาพ")

# ✅ Image handler
async def handle_image(event):
    user_id = event.source.user_id
    selected_state = get_user_state(user_id)

    if not selected_state or not selected_state.startswith("image_"):
        send_message(event, "⚠️ ยังไม่ได้เลือกบริการ หรือหมดเวลา กรุณาพิมพ์ #img และเลือกบริการก่อนส่งภาพ")
        return

    service_code = selected_state.split("_")[1]

    image_content = line_bot_api.get_message_content(event.message.id)
    image_path = "image.jpg"
    with open(image_path, "wb") as f:
        for chunk in image_content.iter_content():
            f.write(chunk)

    try:
        if service_code == '1':
            result = face_blur.analyze(image_path)
            send_image(event, convert_http_to_https(result['URL']))
        elif service_code == '2':
            result = chest_classification.analyze(image_path, return_json=False)
            send_message(event, result[0]['result'])
        elif service_code == '3':
            result = violence_classification.analyze(image_path)
            send_message(event, result['objects'][0]['result'])
        elif service_code == '4':
            result = nsfw.analyze(image_path)
            send_message(event, result['objects'][0]['result'])
        elif service_code == '5':
            result = super_resolution.analyze(image_path)
            send_image(event, convert_http_to_https(result['url']))
        elif service_code == '6':
            result = person_detection(image_path)
            send_image(event, convert_http_to_https(result))
        elif service_code == '7':
            result = capgen(image_path)
            send_message(event, str(result))
        else:
            send_message(event, "⚠️ ไม่พบบริการที่เลือก")
    except Exception as e:
        send_message(event, f"❗เกิดข้อผิดพลาด: {str(e)}")

    # 🔚 Clear user state after successful image processing
    clear_user_state(user_id)

# ✅ Utility: Send text message
def send_message(event, message):
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))

# ✅ Utility: Send image
def send_image(event, image_url):
    line_bot_api.reply_message(
        event.reply_token,
        ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
    )

# ✅ Utility: Convert HTTP → HTTPS
def convert_http_to_https(url):
    if url.startswith("http://"):
        return url.replace("http://", "https://", 1)
    return url

#### function for person detection api for aiforthai ####
def person_detection(image_dir):
    url = cfg.URL_PERSON_DETEC
    files = {"src_img": open(image_dir, "rb")}  ### input image dir here ###
    data = {"json_export": "true", "img_export": "true"}
    headers = {"Apikey": cfg.AIFORTHAI_APIKEY}

    response = requests.post(url, files=files, headers=headers, data=data)
    response = response.json()["human_img"]
    response = convert_http_to_https(response)
    return response

### function for Image Caption
def capgen(img_path):
    url =cfg.URL_CAPGEN
 
    headers = {'Apikey':cfg.AIFORTHAI_APIKEY}
    
    payload = {}
    files=[
    ('file',(img_path,open(img_path,'rb'),'image/jpeg'))
    ]
    
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    
    # print(response.json())
    return(response.json()["caption"] )

