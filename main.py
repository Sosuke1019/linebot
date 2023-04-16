import os
from app import app, send_message
import schedule
import time
import pytz


# タイムゾーンを設定
app.config['TIMEZONE'] = 'Asia/Tokyo'
timezone = pytz.timezone(app.config['TIMEZONE'])

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)

    # 毎日12時にsend_message関数を実行するようスケジュールを設定
    schedule.every().day.at("13:42").do(send_message)

    #タイマーを回す
    while True:
        # スケジュールされたタスクを実行する
        schedule.run_pending()
        # 1秒待機
        time.sleep(1)