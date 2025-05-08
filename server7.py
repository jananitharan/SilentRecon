from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
from datetime import datetime
from user_agents import parse

app = Flask(__name__, static_folder='static')
CORS(app)

log_file = '/var/www/html/location_logs.txt'
IPINFO_TOKEN = "8c17328db2174a"  

@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/receive_location', methods=['GET'])
def receive_location():
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
        user_agent_str = request.headers.get('User-Agent')
        user_agent = parse(user_agent_str)

        location_info = {
            "ip": client_ip,
            "hostname": "N/A",
            "city": "N/A",
            "region": "N/A",
            "country": "N/A",
            "loc": "N/A",
            "org": "N/A",
            "postal": "N/A",
            "timezone": "N/A",
            "anycast": False,
            "browser": user_agent.browser.family,
            "browser_version": user_agent.browser.version_string,
            "os": user_agent.os.family,
            "os_version": user_agent.os.version_string,
            "device": user_agent.device.family,
            "referrer": request.referrer,
            "screen_resolution": request.args.get('screen', 'N/A'),
            "timezone_offset": request.args.get('timezone', 'N/A'),
            "touch_support": user_agent.is_touch_capable
        }

        try:
            response = requests.get(
                f"https://ipinfo.io/{client_ip}/json",
                headers={"Authorization": f"Bearer {IPINFO_TOKEN}"},
                timeout=5
            )

            if response.status_code == 200:
                geo_data = response.json()
                location_info.update(geo_data)
            else:
                location_info["error"] = f"API Error: {response.status_code} - {response.text}"

        except requests.exceptions.RequestException as e:
            location_info["error"] = f"API Request Error: {str(e)}"

        log_entry = {
            "timestamp": timestamp,
            "location_info": location_info
        }

        with open(log_file, 'a') as f:
            f.write(f"{log_entry}\n")

        return jsonify(log_entry)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory('static/images', filename)

@app.route('/script.obfuscated.js')
def serve_script():
    return send_from_directory('static', 'script.obfuscated.js')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

print("______________________________________________________")
