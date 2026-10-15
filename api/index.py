from flask import Flask, request, jsonify
import requests
import jwt
import urllib3
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ReqCLan_pb2

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
OB = "OB55"

KEY = bytes([89,103,38,116,99,37,68,69,117,104,54,37,90,99,94,56])
IV  = bytes([54,111,121,90,68,114,50,50,69,51,121,99,104,106,77,37])

REGION_SERVER_MAP = {
    "IND": "https://client.ind.freefiremobile.com",
    "ME":  "https://clientbp.ggpolarbear.com",
    "BD":  "https://clientbp.ggpolarbear.com",
    "PK":  "https://clientbp.ggpolarbear.com",
    "VN":  "https://clientbp.ggpolarbear.com",
    "SG":  "https://clientbp.ggpolarbear.com",
    "ID":  "https://clientbp.ggpolarbear.com",
    "TH":  "https://clientbp.ggpolarbear.com",
    "RU":  "https://clientbp.ggpolarbear.com",
    "BR":  "https://client.us.freefiremobile.com",
    "NA":  "https://client.us.freefiremobile.com",
    "US":  "https://client.us.freefiremobile.com",
}
DEFAULT_SERVER_URL = "https://clientbp.ggpolarbear.com"


def encrypt_payload(data):
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    return cipher.encrypt(pad(data, AES.block_size))


def decode_jwt(token):
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        return str(decoded.get("account_id")), decoded.get("nickname"), decoded.get("lock_region")
    except Exception as e:
        print(f"JWT error: {e}")
        return None, None, None


def get_server_url(region):
    if not region:
        return DEFAULT_SERVER_URL
    return REGION_SERVER_MAP.get(region.upper(), DEFAULT_SERVER_URL)


def get_jwt_from_uid_password(uid, password):
    url = f"https://ff-jwt-web-api-iota.vercel.app/token?uid={uid}&password={password}"
    try:
        r = requests.get(url, timeout=25)
        data = r.json()
        if data.get("status") == "success" and "token" in data:
            jwt_token = data["token"]
            account_id, nickname, region = decode_jwt(jwt_token)
            return jwt_token, account_id, nickname, region
        return None, None, None, None
    except Exception as e:
        print(f"JWT API error: {e}")
        return None, None, None, None


def request_clan(jwt_token, clan_id, region):
    server_url = get_server_url(region)
    url = f"{server_url}/RequestJoinClan"
    
    msg = ReqCLan_pb2.MyMessage()
    msg.field_1 = int(clan_id)
    payload = encrypt_payload(msg.SerializeToString())
    
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/octet-stream",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; en-US; SM-G975F Build/PPR1.180610.011)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": OB,
        "Expect": "100-continue"
    }
    
    try:
        r = requests.post(url, headers=headers, data=payload, verify=False, timeout=20)
        return r.status_code, r.text
    except Exception as e:
        return 0, str(e)


@app.route("/")
def home():
    return jsonify({
        "success": True,
        "message": "FF Guild Join API",
        "usage": "/guildid=CLAN_ID&uid=UID&pass=PASSWORD",
        "example": "/guildid=3055499648&uid=7938049484&pass=YOUR_PASS",
        "developer": "@STAR_GMR",
        "telegram": "@PVT_STAR"
    })


@app.route("/guildid=<int:clan_id>&uid=<uid>&pass=<password>")
def join_guild(clan_id, uid, password):
    jwt_token, real_uid, nickname, region = get_jwt_from_uid_password(uid, password)
    
    if not jwt_token:
        return jsonify({
            "success": False,
            "error": "JWT generation failed - Check UID/Password",
            "uid": uid,
            "guild_id": clan_id
        }), 400
    
    code, text = request_clan(jwt_token, clan_id, region)
    
    return jsonify({
        "success": code == 200,
        "action": "Join Guild",
        "guild_id": clan_id,
        "input_uid": uid,
        "real_uid": real_uid,
        "nickname": nickname,
        "region": region,
        "server_url": get_server_url(region),
        "http_status": code,
        "server_response": text[:500] if text else "Empty",
        "developer": "@STAR_GMR",
        "telegram": "@PVT_STAR"
    })


@app.route("/join")
def join_guild_query():
    clan_id = request.args.get("guildid") or request.args.get("clan_id")
    uid = request.args.get("uid")
    password = request.args.get("pass") or request.args.get("password")
    
    if not all([clan_id, uid, password]):
        return jsonify({"success": False, "error": "guildid, uid, pass required"}), 400
    
    return join_guild(int(clan_id), uid, password)
