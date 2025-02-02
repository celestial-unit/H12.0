from flask import Blueprint, request, jsonify
import requests

chatbot_bp = Blueprint("chatbot", __name__)

CHATBOT_URL = "https://www.chatbase.co/chatbot-iframe/qPdrlF_8zHkqezOLeASnB"

@chatbot_bp.route("/chat", methods=["POST"])
def chat():
    user_message = request.form.get("message")

    if not user_message:
        return jsonify({"error": "Message not provided"}), 400

    response = requests.post(CHATBOT_URL, json={"message": user_message})

    if response.status_code == 200:
        chatbot_reply = response.json().get("response", "I didn't understand.")
        return jsonify({"reply": chatbot_reply})
    else:
        return jsonify({"error": "Error communicating with chatbot"}), 500
