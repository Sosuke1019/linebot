import os
from typing import Dict

from dotenv import load_dotenv
from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, Source, TextMessage, TextSendMessage

from .gpt.client import ChatGPTClient
from .gpt.constants import Model, Role
from .gpt.message import Message


load_dotenv(".env", verbose=True)


app = Flask(__name__)


#環境変数取得
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

chatgpt_instance_map: Dict[str, ChatGPTClient] = {}


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event: MessageEvent) -> None:
    text_message: TextMessage = event.message
    source: Source = event.source
    user_id: str = source.user_id

    if (gpt_client := chatgpt_instance_map.get(user_id)) is None:
        gpt_client = ChatGPTClient(model=Model.GPT35TURBO)
    
    gpt_client.add_message(
        message=Message(role=Role.USER, content=text_message.text)
    )
    res = gpt_client.create()
    chatgpt_instance_map[user_id] = gpt_client

    res_text: str = res["choices"][0]["message"]["content"]

    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text=res_text.strip())
    )

