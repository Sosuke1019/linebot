import os
from typing import Dict

from dotenv import load_dotenv
from flask import Flask, request, abort
import schedule
import datetime

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, Source, TextMessage, TextSendMessage, TemplateSendMessage

from .gpt.client import ChatGPTClient
from .gpt.constants import Model, Role
from .gpt.message import Message


load_dotenv(".env", verbose=True)


app = Flask(__name__)


# 環境変数取得
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

chatgpt_instance_map: Dict[str, ChatGPTClient] = {}


# 通知を送る関数
def send_message():
    message = TextSendMessage(text="面接練習を行いたい場合は、「面接練習する」と送信してください。")
    # メッセージを送信
    line_bot_api.broadcast(message)


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

    # system_message = Message(role=Role.SYSTEM, content="あなたはドラゴンボールの孫悟空です。悟空の口調で回答してください。第一人称はオラです。")
    system_message = Message(role=Role.SYSTEM, content="あなたは新卒採用を行う面接官です。あなたは日本のIT業界に所属しています。1回返答を受けたら、返す質問は必ず一つにしてください。")
    gpt_client.add_message(system_message)

    
    if text_message.text == "面接練習する":
        template = {
            "type": "confirm",
            "text": "①面接官の性別",
            "actions": [
                {"type": "message", "label": "男性", "text": "男性"},
                {"type": "message", "label": "女性", "text": "女性"},
            ],
        }
        message = {"type": "template", "altText": "代替テキスト", "template": template}
        message_list = [
            TextSendMessage(text="ありがとうございます! 面接に必要となる情報を教えてください!①面接官の性別②あなたのプロフィール)"),
            TemplateSendMessage.new_from_json_dict(message),
        ]
        line_bot_api.reply_message(event.reply_token, message_list)

    if text_message.text in {"男性", "女性"}:
        user_profile = text_message.text + "として振る舞ってください。"
        system_message = Message(role=Role.SYSTEM, content= user_profile)
        gpt_client.add_message(system_message)
        line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text="②プロフィール(例：名前:竹田花子, 性別:女性, 学年:3年生, 学部:情報学部, 志望企業:Google)の入力を行ってください。")
        )
        return

    gpt_client.add_message(
        message=Message(role=Role.USER, content=text_message.text)
    )

    res = gpt_client.create()
    chatgpt_instance_map[user_id] = gpt_client

    res_text: str = res["choices"][0]["message"]["content"]

    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text=res_text.strip())
    )

