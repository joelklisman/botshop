import os
import logging
from flask import Flask, request, jsonify
from telegram import Bot

# --- Load environment variables ---
from dotenv import load_dotenv
load_dotenv()

# --- Setup ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "8377595320:AAEuRtqXFDhJaKz2ROjbzg6LNLXYnB-JTJE")
bot = Bot(token=BOT_TOKEN)

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

# 🧠 Temporary in-memory store to map order_id ↔ chat_id
# (You can update this dynamically from bot.py)
ORDER_CHAT_MAP = {
    "TG-123456789": 1758873592  # replace with your Telegram user_id
}

# --- ROOT ---
@app.route("/", methods=["GET"])
def home():
    return "✅ Webhook server is running!", 200

# --- NOWPAYMENTS WEBHOOK ---
@app.route("/nowpayments/webhook", methods=["POST"])
def nowpayments_webhook():
    data = request.get_json(force=True)
    logging.info(f"📩 Webhook received: {data}")

    payment_status = data.get("payment_status")
    order_id = data.get("order_id")
    payment_id = data.get("payment_id")
    pay_amount = data.get("pay_amount")
    pay_currency = data.get("pay_currency")

    logging.info(f"ℹ️ Payment status: {payment_status}")

    # ✅ If payment is finished, send Telegram confirmation
    if payment_status == "finished":
        chat_id = ORDER_CHAT_MAP.get(order_id)
        if chat_id:
            try:
                message = (
                    f"✅ *Payment Confirmed!*\n\n"
                    f"🆔 Order ID: `{order_id}`\n"
                    f"💰 Amount: `{pay_amount} {pay_currency}`\n"
                    f"📦 Status: *{payment_status.title()}*\n\n"
                    f"Thank you for your purchase!"
                )
                bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
                logging.info(f"✅ Sent confirmation to chat_id {chat_id}")
            except Exception as e:
                logging.error(f"❌ Failed to send Telegram message: {e}")
        else:
            logging.warning(f"⚠️ No chat_id mapped for order_id {order_id}")

    return jsonify({"status": "ok"}), 200


# --- Run server ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
