#.gitignoreでバージョン管理から除外する(アクセストークンやチャネルシークレットは、個人情報や重要な情報を含むため、公開された場所に書き込んだり、他人に知られたりしないように注意する必要がある。.envファイルは公開されないようにするために、.gitignoreなどでバージョン管理システムから除外することが一般的。)
#毎回、ngrokのエンドポイントが変わる(ngrokは起動するたびに異なるエンドポイントを発行するため、一度終了したのちに再度起動した場合はLINE DevelopersのWebhookURLもあわせて修正する必要がある)

# やること
# 面接官としてどんな感じでやっていくかをプロンプトで決めておく。(sosuke)
# ユーザーに情報を入力してもらう(sosuke)

# linebotをactiveにする手順
# 1. source venv/bin/activate で仮想環境をactiveにする
# 2. ターミナルでflask run --reload --port 8080を実行する
# 3. 別のターミナルでngrok http 8080を実行し、ngrokを起動してサーバーを外部公開する
# 4. LINE DeveloperのWebhook URLにForwardingと記載の行のhttpsで始まる側のURLをコピーする

from flask import Flask, request, abort
from dotenv import load_dotenv

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os

app = Flask(__name__)

load_dotenv()

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
YOUR_CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

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
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
