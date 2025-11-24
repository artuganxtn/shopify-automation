from flask import Flask, request, jsonify
import hmac
import hashlib
import base64
import json
import os

from sms_api import sendSingleMessage

app = Flask(__name__)

SHOPIFY_SECRET = os.environ.get("SHOPIFY_SECRET")  # Webhook secret


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

    # Example: If cart is created and phone exists → SMS
    if event == "carts/create":
        buyer_phone = data.get("buyer_identity", {}).get("phone")

        if buyer_phone:
            try:
                sendSingleMessage(
                    buyer_phone,
                    "Thank you for visiting! Your cart has been saved 💬"
                )
            except Exception as ex:
                print("SMS Error:", ex)

    return jsonify({"status": "success"}), 200


# -----------------------------
# Deployment Server
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
