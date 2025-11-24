import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env
SERVER = "https://sms-spider.com"
API_KEY = os.environ.get("SMS_API_KEY")

USE_SPECIFIED = 0
USE_ALL_DEVICES = 1
USE_ALL_SIMS = 2

def send_request(url, data):
    response = requests.post(url, data=data)
    json_data = response.json()

    if response.status_code != 200:
        raise Exception(f"HTTP Error Code: {response.status_code}")

    if json_data.get("success"):
        return json_data["data"]
    else:
        raise Exception(json_data["error"]["message"])

def sendSingleMessage(number, message, device=0, schedule=None, isMMS=False, attachments=None, prioritize=False):
    url = f"{SERVER}/services/send.php"
    payload = {
        "number": number,
        "message": message,
        "schedule": schedule,
        "key": API_KEY,
        "devices": device,
        "type": "mms" if isMMS else "sms",
        "attachments": attachments,
        "prioritize": 1 if prioritize else 0,
    }
    return send_request(url, payload)["messages"][0]

