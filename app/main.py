import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # For Vaja9
from app import service_webhook, service_main, service_nlp, service_image  # 👈 import ตัวใหม่

# from app import (
#     service_main,  # main service router
#     service_nlp,  # NLP service router
# )

app = FastAPI(
    title="aiforthai-line-chatbot",
    description="AIFORTHAI LINE CHATBOT WORKSHOP",
    version="1.0.0",
)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(service_webhook.router)
app.include_router(service_main.router)
app.include_router(service_nlp.router)
app.include_router(service_image.router)

# Save static files at the /static endpoint
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static/", StaticFiles(directory="static"), name="static")

@app.get("/")
def index():
    return "AIFORTHAI LINE CHATBOT WORKSHOP"