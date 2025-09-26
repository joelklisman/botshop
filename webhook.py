import os
import logging
from flask import Flask, request, jsonify
from telegram import Bot

# Load environment
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

app = Flask(__name__)

# Logging
logging.basicConfig(level=logging.INFO)

@app.route("/")
def home():
    return "✅ Bot Webhook Server is Running!", 200

@app.route("/health")
def health():
    return "OK", 200

# NowPayments webhook endpoint
@app.route("/nowpayments/webhook", methods=["POST"])
def nowpayments_webhook():
    data = request.json
    logging.info(f"📩 Webhook received: {data}")

    try:
        payment_status = data.get("payment_status")
        order_id = data.get("order_id", "")
        payment_id = data.get("payment_id", "")
        pay_amount = data.get("pay_amount", "?")
        pay_currency = data.get("pay_currency", "?")

        # Extract Telegram user ID if you included it in order_id (optional)
        # Example order_id: "TG-<user_id>-<timestamp>"
        chat_id = None
        if order_id.startswith("TG-"):
            parts = order_id.split("-")
            if len(parts) > 2 and parts[1].isdigit():
                chat_id = int(parts[1])

        # Only send confirmation when finished
        if payment_status == "finished" and chat_id:
            bot.send_message(
                chat_id=chat_id,
                text=(
                    f"✅ Payment confirmed!\n"
                    f"💰 Amount: {pay_amount} {pay_currency}\n"
                    f"🆔 Payment ID: {payment_id}\n\n"
                    f"Thank you for your order 🎉"
                )
            )
            logging.info(f"✅ Confirmation sent to user {chat_id}")
        else:
            logging.info(f"ℹ️ Payment status: {payment_status}")

    except Exception as e:
        logging.error(f"❌ Error handling webhook: {e}")

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
