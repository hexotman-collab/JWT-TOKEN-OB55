import time
import uuid
import random
import json
import requests
import urllib3
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from google_play_scraper import app as gp_app
from flask import Flask, request, jsonify

# ⚠️ يجب أن يكون MajorLogin_pb2.py موجوداً في نفس المجلد
import MajorLogin_pb2

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

ak = b'Yg&tc%DEuh6%Zc^8'
aiv = b'6oyZDr22E3ychjM%'

# ⚠️ ضع بيانات الحساب هنا أو استخدم متغيرات البيئة
import os
accUID = os.environ.get("FF_UID", "(:")
accPASSWORD = os.environ.get("FF_PASSWORD", "(:")


def encryptapi(plainbytes):
    cipher = AES.new(ak, AES.MODE_CBC, aiv)
    return cipher.encrypt(pad(plainbytes, AES.block_size))


def GuestLogin(uid, password):
    url = "https://100067.connect.garena.com/api/v2/oauth/guest/token:grant"
    header = {
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
        "Host": "100067.connect.garena.com",
        "User-Agent": "GarenaMSDK/4.0.42(A5010 ;Android 9;en;US;app 2.126.1 2019118045;)"
    }
    payload = {
        "client_id": 100067,
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_type": 2,
        "device_id": "02-" + str(uuid.uuid4()),
        "password": str(password),
        "response_type": "token",
        "uid": int(uid)
    }
    reg = requests.post(url, headers=header, data=json.dumps(payload), timeout=8)
    if reg.status_code == 200:
        res = reg.json()
        if res.get('code') == 0:
            return res['data']['access_token'], res['data']['open_id'], res['data']['platform']
    return None, None, None


def MajorLogin(access_token, open_id, platform, server_url, obb, remote_version, vercfg_sign):
    payload = MajorLogin_pb2.MajorLoginRequest(
        Field3=time.strftime("%Y-%m-%d %H:%M:%S"),
        Field4="free fire",
        Field5=1,
        Field7=remote_version,
        Field8="Android OS 14 / API-34",
        Field9="Handheld",
        Field10="Mobilis",
        Field11="WIFI",
        Field12=1600,
        Field13=900,
        Field14="240",
        Field15="x86-64 SSE3 SSE4.1 SSE4.2 AVX | 2865 | 6",
        Field16=5944,
        Field17="Adreno (TM) 750",
        Field18="OpenGL ES 3.1 v1",
        Field19=f"Google|{uuid.uuid4()}",
        Field20=f"{random.randint(1,223)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
        Field21="pt-br",
        Field22=str(open_id),
        Field23=str(platform),
        Field24="Handheld",
        Field25="samsung SM-N9860",
        Field29=str(access_token),
        Field30=1,
        Field41="Mobilis",
        Field42="WIFI",
        Field57="7428b253defc164018c604a1ebbfebdf",
        Field60=52691,
        Field61=48409,
        Field62=2519,
        Field63=70,
        Field64=23306,
        Field65=25131,
        Field66=50733,
        Field67=52691,
        Field73=3,
        Field74="/data/app/lib/arm64",
        Field76=1,
        Field77="b8e0cd5e295eee42f5860d3c86e483dd|/data/app/base.apk",
        Field78=3,
        Field79=2,
        Field81="64",
        Field83="2019121229",
        Field85=3,
        Field86="OpenGLES2",
        Field87=8191,
        Field88=4,
        Field89="KqsHT6dXfrd81vpmdClMMxZM3UCc59ys5/2cX5FVcMpI3tlWy8d0r8ZWGSBj+06/cGbBzY3JULeYT1rb5tBtz7+GCis6kpkGPjl2SSoYhrjsQOvA",
        Field92=7303,
        Field93="android",
        Field94="KqsHT6dXfrd81vpmdClMMxZM3UCc59ys5/2cX5FVcMpI3tlWy8d0r8ZWGSBj+06/cGbBzY3JULeYT1rb5tBtz7+GCis6kpkGPjl2SSoYhrjsQOvA",
        Field95=111207,
        Field96='{"cur_rate":null,"support_etc2":false}',
        Field97=1,
        Field98=1,
        Field99=str(platform),
        Field100=str(platform),
        Field102=b"",
        Field104=62270,
        Field105=1,
        Field106="https://dl.gmc.freefiremobile.com/live/ABHotUpdates/|https://core-gmc.freefiremobile.com/live/ABHotUpdates/|4a0070ac356973792f002e0b25b96c3b",
        Field107=vercfg_sign
    )
    plain = payload.SerializeToString()
    encpayload = encryptapi(plain)

    url = server_url + "MajorLogin"
    header = {
        'X-Unity-Version': '2018.4.11f1',
        'ReleaseVersion': obb,
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-GA': 'v1 1',
        'X-GA-SV': '1790794556',
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }

    reg = requests.post(url, headers=header, data=encpayload, timeout=8)
    if reg.status_code == 200:
        login = MajorLogin_pb2.MajorLoginResponse()
        login.ParseFromString(reg.content[64:] if len(reg.content) > 64 else reg.content)
        return login
    return None


@app.route('/', methods=['GET', 'POST'])
def index():
    return jsonify({
        "status": "online",
        "usage": "أضف /login?uid=YOUR_UID&password=YOUR_PASS أو أرسل POST JSON",
        "example_get": "/login?uid=123456789&password=abc123",
        "example_post": {"uid": "123456789", "password": "abc123"}
    })


@app.route('/login', methods=['GET', 'POST'])
def login_route():
    # قراءة البيانات من الطلب
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        uid = data.get('uid') or accUID
        password = data.get('password') or accPASSWORD
    else:
        uid = request.args.get('uid') or accUID
        password = request.args.get('password') or accPASSWORD

    if uid == "(:": 
        return jsonify({
            "status": "error",
            "message": "لم يتم تحديد UID/Password. أرسل ?uid=...&password=... أو اضبط متغيرات البيئة FF_UID و FF_PASSWORD"
        }), 400

    try:
        # 1) جلب إصدارات اللعبة
        lib = gp_app('com.dts.freefireth', lang='en', country='us')['version']
        obb = requests.get(
            "https://version.ggwhitehawk.com/live/ver.php?lang=en&device=android",
            timeout=8
        ).json()["latest_release_version"]

        ggwhiteawk = requests.get(
            f"https://version.ggwhitehawk.com/live/ver.php?version={lib}"
            f"&lang=en&device=android&channel=android&appstore=googleplay"
            f"&region=BD&release_version={obb}&whitelist_version=1.8.0"
            f"&whitelist_sp_version=1.0.0&device_name=OPPO%20PHM110"
            f"&device_CPU=x86-64%20SSE3%20SSE4.1%20SSE4.2%20AVX"
            f"&device_GPU=Adreno%20%28TM%29%20750&device_mem=3004",
            timeout=8
        ).json()

        server_url = ggwhiteawk["server_url"]
        obb = ggwhiteawk["latest_release_version"]
        remote_version = ggwhiteawk["remote_version"]
        vercfg_sign = ggwhiteawk["vercfg_sign"]

        # 2) تسجيل الدخول كضيف
        access_token, open_id, platform = GuestLogin(uid, password)
        if not access_token:
            return jsonify({
                "status": "error",
                "message": "فشل تسجيل الدخول كضيف (GuestLogin). تحقق من UID/Password."
            }), 401

        # 3) MajorLogin
        response = MajorLogin(access_token, open_id, platform,
                              server_url, obb, remote_version, vercfg_sign)
        if not response:
            return jsonify({"status": "error", "message": "فشل MajorLogin"}), 500

        # محاولة تحويل النتيجة إلى dict إن أمكن
        try:
            from google.protobuf.json_format import MessageToDict
            result = MessageToDict(response)
        except Exception:
            result = str(response)

        return jsonify({
            "status": "success",
            "open_id": open_id,
            "platform": platform,
            "access_token": access_token,
            "response": result
        })

    except Exception as e:
        return jsonify({"status": "error", "message": f"{type(e).__name__}: {e}"}), 500


# Vercel يحتاج إلى متغير باسم app أو application
application = app