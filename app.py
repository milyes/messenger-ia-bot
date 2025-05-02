from flask import Flask, request
import openai
import requests
import os

app = Flask(__name__)

VERIFY_TOKEN = open("verify_token.txt").read().strip()
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Invalid verification token", 403

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    message_text = messaging_event["message"].get("text")

                    if message_text:
                        response = openai.ChatCompletion.create(
                            model="gpt-4",
                            messages=[{"role": "user", "content": message_text}]
                        )
                        reply = response.choices[0].message["content"]
                        send_message(sender_id, reply)
    return "OK", 200

def send_message(recipient_id, message_text):
    url = "https://graph.facebook.com/v18.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    requests.post(url, params=params, headers=headers, json=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
