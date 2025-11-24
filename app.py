from flask import Flask, request, jsonify
import hmac
import hashlib
import base64
import json
import os
from datetime import datetime, timedelta
from sms_api import sendSingleMessage

app = Flask(__name__)

# -----------------------------
# Environment Variables
# -----------------------------
SHOPIFY_SECRET = os.environ.get("SHOPIFY_SECRET")  # Webhook secret
SMS_SENDER_DEVICE = int(os.environ.get("SMS_DEVICE", 0))  # SMS-Spider device ID

# -----------------------------
# Verify Shopify Webhook
# -----------------------------
def verify_webhook(req):
    received_hmac = req.headers.get("X-Shopify-Hmac-Sha256")
    calculated_hmac = base64.b64encode(
        hmac.new(
            SHOPIFY_SECRET.encode("utf-8"),
            req.data,
            hashlib.sha256
        ).digest()
    ).decode("utf-8")

    return hmac.compare_digest(received_hmac, calculated_hmac)

# -----------------------------
# Test Route
# -----------------------------
@app.get("/")
def home():
    return "Shopify SMS Automation is running! 🚀"

# -----------------------------
# Helper: Send SMS
# -----------------------------
def send_sms(phone, message):
    try:
        sendSingleMessage(phone, message, device=SMS_SENDER_DEVICE)
        print(f"✅ SMS sent to {phone}: {message}")
    except Exception as e:
        print(f"❌ SMS error for {phone}: {e}")

# -----------------------------
# Webhook Endpoint
# -----------------------------
@app.post("/shopify/webhook")
def shopify_webhook():
    if not verify_webhook(request):
        return jsonify({"error": "Invalid webhook signature"}), 401

    data = request.json
    event = request.headers.get("X-Shopify-Topic")

    print("📩 Received Shopify Event:", event)
    print("📦 Payload:", json.dumps(data, indent=2))

    # -----------------------------
    # Order Created (Paid/Confirmed)
    # -----------------------------
    if event in ["orders/create", "orders/paid"]:
        buyer_name = data.get("customer", {}).get("first_name", "")
        buyer_phone = data.get("customer", {}).get("phone")

        if buyer_phone:
            message = f"مرحباً {buyer_name}، شكراً لطلبك! تم تأكيد طلبك وسيتم شحنه قريباً 🚚"
            send_sms(buyer_phone, message)

    # -----------------------------
    # Order Fulfilled / Shipped
    # -----------------------------
    if event == "orders/fulfilled":
        buyer_name = data.get("customer", {}).get("first_name", "")
        buyer_phone = data.get("customer", {}).get("phone")

        if buyer_phone:
            message = f"مرحباً {buyer_name}، طلبك الآن في الطريق! 📦 شكراً لاختيارك متجرنا."
            send_sms(buyer_phone, message)

    return jsonify({"status": "success"}), 200

# -----------------------------
# Deployment Server
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
