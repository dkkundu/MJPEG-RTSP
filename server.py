import os
from flask import Flask, Response
from dotenv import load_dotenv
import requests
import cv2
load_dotenv()
app = Flask(__name__)

FIXED_TOKEN = "DK12LIVEstr66Go"
MFR_SERVER = "http://192.168.68.176:9000"

# CORS headers configuration
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    return response

def call_external_api(company_id, device_id):
    try:
        url = f'{MFR_SERVER}/api/v1/device/camera-device/'
        payload = {
            "token": FIXED_TOKEN,
            "company": company_id,
            "device_id": device_id
        }
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print("Error occurred:", e)
        return None


def generate_mjpeg(rtsp_url):
    cap = cv2.VideoCapture(rtsp_url)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        # Encode the frame in JPEG format
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        # Yield the JPEG frame
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

    cap.release()

@app.route('/video-streaming/<path:company_id>/<path:device_id>/')
def video_feed(company_id, device_id):
    try:
        result = call_external_api(company_id, device_id)
        stream_address = None
        if result:
            stream_address = result['data']['stream_address']
        return Response(generate_mjpeg(stream_address), mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print("Error occurred:", e)
    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
