# QuinticSolverBot (All-in-One)
import time
import requests
import json
import os

TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
URL = f"https://api.telegram.org/bot{TOKEN}/"

def get_updates(offset=None):
    params = {"timeout": 30, "offset": offset}
    try:
        response = requests.get(URL + "getUpdates", params=params, timeout=35)
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return {}

def send_message(chat_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    try:
        requests.post(URL + "sendMessage", data=data)
    except Exception as e:
        print(f"Error sending message: {e}")

def main():
    print("QuinticSolverBot запущен...")
    offset = None
    while True:
        updates = get_updates(offset)
        if "result" in updates:
            for update in updates["result"]:
                offset = update["update_id"] + 1
                if "message" in update:
                    message = update["message"]
                    chat_id = message.get("chat", {}).get("id")
                    text = message.get("text", "")
                    if text.startswith("/start"):
                        send_message(chat_id, "Привет! Я бот для вычислений.")
                    else:
                        send_message(chat_id, f"Вы написали: {text}")
        time.sleep(0.5)

if __name__ == "__main__":
    main()
