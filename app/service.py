from fastapi import APIRouter, Request

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage, AudioSendMessage,AudioMessage

from aift import setting
from aift.multimodal import textqa
from aift.image.classification import maskdetection

from datetime import datetime

# AIForThai import
from aift.nlp import tokenizer # 1. Tokenizer
from aift.nlp import ner # 1.1 TNER
from aift.nlp import g2p # 2. G2P
from aift.nlp import soundex # 3. Soundex
from aift.nlp import similarity # 4. Word similarity
from aift.nlp import text_cleansing # 5. Text cleasing
from aift.nlp import tag # 6. Tag Suggestion
from aift.nlp.translation import zh2th # 7.1. Chinese to Thai
from aift.nlp.translation import th2zh # 7.2. Thai to Chinese
from aift.nlp.translation import en2th # 7.3. English to Thai
from aift.nlp.translation import th2en # 7.4. Thai to English
from aift.nlp import sentiment # 8. Sentiment analysis
from aift.nlp.longan import sentence_tokenizer, tagger, token_tagger, tokenizer as logan_tokenizer # 9. Longan
from aift.nlp.alignment import en_alignment # 10.1. English-Thai Word Aligner
from aift.nlp.alignment import zh_alignment # 10.2. Chinese-Thai Word Aligner
from aift.speech import tts

# For Partii STT
import io
import json
import requests

# For Vaja9
import wave

from app.configs import Configs

router = APIRouter(tags=[""])

cfg = Configs()

setting.set_api_key(cfg.AIFORTHAI_APIKEY)  # AIForThai API key
LINE_CHANNEL_ACCESS_TOKEN = LineBotApi(cfg.LINE_CHANNEL_ACCESS_TOKEN) #LINE Channel Access Token from developers page (https://developers.line.biz/en/)
LINE_CHANNEL_SECRET = WebhookHandler(cfg.LINE_CHANNEL_SECRET) # Channel Secret from developers page (https://developers.line.biz/en/)

URL = "" # URL ต้องมีเครื่องหมาย "/" ปิดท้ายด้วย ตัวอย่าง เช่น https://xszqqc8g-8000.asse.devtunnels.ms/
WAV_FILE = "file.wav"
DIR_FILE = "static/"

setting.set_api_key(AIFORTHAI_APIKEY)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)  # CHANNEL_ACCESS_TOKEN
handler = WebhookHandler(LINE_CHANNEL_SECRET)  # CHANNEL_SECRET


@router.post("/message")
async def hello_word(request: Request):
    signature = request.headers["X-Line-Signature"]
    body = await request.body()
    try:
        handler.handle(body.decode("UTF-8"), signature)
    except InvalidSignatureError:
        print(
            "Invalid signature. Please check your channel access token or channel secret."
        )
    return "OK"

@handler.add(MessageEvent, message=AudioMessage)
def handle_voice_message(event):
    # #14. SPEECH TO TEXT (Partii)
    # Get the audio file from LINE
    message_content = line_bot_api.get_message_content(event.message.id)
    
    # Save the audio content to a file (optional, for further processing)
    with open("received_audio.wav", "wb") as f:
        for chunk in message_content.iter_content():
            f.write(chunk)
        
    text = callPartii("received_audio.wav")
    send_message(event,str(text))

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = ''
    # # อันดับแรกต้องเปิดทำการส่งข้อความใน ข้อ 11. หากใช้ Vaja ให้ปิดในข้อ 11.

    # #1. Tokeninzer
    #TLex+, Lexto+
    # text = tokenizer.tokenize(event.message.text, engine='trexplus', return_json=True) # TLex+
    # text = tokenizer.tokenize(event.message.text, engine='lexto', return_json=True) # Lexto+

    # #TLex++
    # res = tokenizer.tokenize(event.message.text, engine='trexplusplus', return_json=True)
    # text = list(zip(res['words'],res['tags']))


    # #TNER
    # res = ner.analyze(event.message.text, return_json=True)
    # text = list(zip(res['words'], res['POS'], res['tags']))
   

    # #2. G2P
    # text = g2p.analyze(event.message.text)['output']['result']

    # #3. Soundex
    # text = soundex.analyze(event.message.text, model='personname')['words'] # model = personname, royin
  
    # #4. Word similarity
    # text = similarity.similarity(event.message.text,engine='thaiwordsim') # engine = thaiwordsim, wordapprox
    # text = similarity.similarity(event.message.text, engine='thaiwordsim', model='thwiki') # model = thwiki, twitter
    # text = similarity.similarity(event.message.text, engine='wordapprox', model='food', return_json=True) # model = personname, royin, food

    # #5. Text cleasing
    # text = text_cleansing.clean(event.message.text)

    # #6. Tag suggestion
    # text = tag.analyze(event.message.text, numtag=5)

    # #7. Machine Translation
    # #7.1. Chinese to Thai
    # #print(event.message.text)
    # text = zh2th.translate(event.message.text, return_json=True)

    # #7.2. Thai to Chinese
    # text = th2zh.translate(event.message.text, return_json=True)

    # #7.3. English to Thai
    # text = en2th.translate(event.message.text)

    # #7.4. Thai to English
    # text = th2en.translate(event.message.text) #{'translated_text': 'kanchanaburihasalookattheclassofkalasin,a320-bedbuswithapremium.'}

    # #8. Sentiment Analysis
    # text = sentiment.analyze(event.message.text) # engine = ssense, emonews, thaimoji, cyberbully
    # text = sentiment.analyze(event.message.text, engine='emonews')
    # text = sentiment.analyze(event.message.text, engine='thaimoji')
    # text = sentiment.analyze(event.message.text, engine='cyberbully')
    
    # #9. Longan
    # #9.1. Sentence Token
    # text = sentence_tokenizer.tokenize(event.message.text)

    # #9.2. Tagger
    # text = tagger.tag(event.message.text)

    # #9.3. Token Tagger
    # text = token_tagger.tokenize_tag(event.message.text)

    # #9.4. Tokenizer
    # text = logan_tokenizer.tokenize(event.message.text)

    # #10. Alignment
    # content = event.message.text.split('|') # รับข้อความจาก Line ในรูปแบบคู่ภาษาที่ต้องการจับคู่ ด้วยเครื่องหมาย "|" 
    # # ตัวอย่างภาษาอังกฤษ-ไทย เช่น "I like to recommend my friends to Thai restaurants|ฉันชอบแนะนำเพื่อนไปร้านอาหารไทย"
    # # ตัวอย่างภาษาจีน-ไทย เช่น "我是10月10日从泰国来的。|ฉันมาจากประเทศไทยเมื่อวันที่ 10 เดือนตุลาคม"

    # #10.1 English-Thai Word Aligner
    # text = en_alignment.analyze(content[0], content[1], return_json=True)

    # #10.2.  Chinese-Thai Word Aligner
    # text = zh_alignment.analyze(content[0], content[1])

    #11. send text message to response
    send_message(event,str(text)) # หากทำข้อการส่งข้อความข้อ 1-11 ให้เปิดใช้งานการส่งข้อความตอบกลับทาง Line

    # #12. Vaja TTS (ก่อนเรียกใช้ Vaja ให้ปิดข้อ 11. และเปิดข้อ 13.ให้เรียบร้อยก่อน)
    # #12.1 Vaja9 case เรียกใช้ผ่าน PIP package (ไม่สามารถกำหนดเสียงได้ จะได้เสียงเป็นผู้ชาย)
    
    # tts.convert(event.message.text, DIR_FILE+WAV_FILE, speaker=0) #[0=เสียงผู้ชาย, 1=เสียงผู้หญิง, 2=เด็กผู้ชาย, 3=เด็กผู้หญิง]
    # audio_url = URL+DIR_FILE+WAV_FILE
    # audio_duration = get_wav_duration_in_ms(DIR_FILE+WAV_FILE)

    # audio_message = AudioSendMessage(
    #         original_content_url=audio_url,
    #         duration=audio_duration
    #     )
    

    # # 12.2 Vaja9 case เรียกใช้งานผ่านฟังก์ชันที่เขียนขึ้นมา สามารถกำหนดเสียงได้ 
    # speaker = 0 #[0=เสียงผู้ชาย, 1=เสียงผู้หญิง, 2=เด็กผู้ชาย, 3=เด็กผู้หญิง]
    # response = callVaja9(event.message.text, speaker)
    
    # if(response.json()['msg'] == 'success'):
        
    #     # Download file and write in .m4a
    #     download_and_play(response.json()['wav_url'])

    #     # Path to the audio file you want to send
    #     audio_url = URL+DIR_FILE+WAV_FILE
    #     print(audio_url)
    #     audio_durations = int(response.json()['durations']*1000)  # Duration in milliseconds (e.g., 5000 milliseconds)
    #     print(audio_durations)

    #     # Create an AudioSendMessage instance
    #     audio_message = AudioSendMessage(
    #         original_content_url=audio_url,
    #         duration=audio_durations
    #     )

    # #13. return audio message response
    # send_audio_message(event,audio_message)  


@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    message_id = event.message.id
    image_content = line_bot_api.get_message_content(message_id)

    # Save the image locally and process it
    with open("image.jpg", "wb") as f:
        for chunk in image_content.iter_content():
            f.write(chunk)

    # aiforthai maskdetection
    result = maskdetection.analyze("image.jpg", return_json=False)
    result = result[0]["result"]

    # return text response
    send_message(event, result)


def echo(event):
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text=event.message.text)
    )

# function for sending audio message
def send_audio_message(event,audio_message):
        line_bot_api.reply_message(
            event.reply_token,
            audio_message)
        
# function for sending message
def send_message(event, message):
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))

def get_wav_duration_in_ms(file_path):
    with wave.open(file_path, 'r') as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        duration = int(frames / rate) * 1000  # Convert seconds to milliseconds
        return duration

# Function call Vaja9
def callVaja9(text, speaker):
    url = 'https://api.aiforthai.in.th/vaja9/synth_audiovisual'

    headers = {'Apikey':AIFORTHAI_APIKEY,"Content-Type": "application/json"}
    data = {'input_text':text,'speaker': speaker}
    response = requests.post(url, json=data, headers=headers)
    return response

# Function for download audio file
def download_and_play(sWav_url):
    file_name = DIR_FILE+WAV_FILE
    with open(file_name, 'wb') as a:
        resp = requests.get(sWav_url,headers={'Apikey':AIFORTHAI_APIKEY})
        # print(resp.status_code)
        if resp.status_code == 200:
            a.write(resp.content)
            #   print('Downloaded: '+sWav_url)
        else:
            print(resp.reason)
            exit(1)
    # return file_name
    
def get_wav_duration_in_ms(file_path):
    with wave.open(file_path, 'r') as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        duration = (frames / rate) * 1000  # Convert seconds to milliseconds
        return duration

# Function for call Partii
def callPartii(file):
    url = "https://api.aiforthai.in.th/partii-webapi"

    files = {'wavfile': (file, open(file, 'rb'), 'audio/wav')}

    headers = {
            'Apikey': AIFORTHAI_APIKEY,
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            }

    param = {"outputlevel":"--uttlevel","outputformat":"--txt"}

    response = requests.request("POST", url, headers=headers, files=files, data=param)
    data = json.loads(response.text)
    return data['message']