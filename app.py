import os
from flask import Flask, request, jsonify, send_from_directory, abort
from flask_cors import CORS
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__, static_folder=None)
CORS(app)

# Only these file types are served from the project root - keeps app.py,
# requirements.txt, .git, .venv, logs, etc. off the public web server.
ALLOWED_STATIC_EXTENSIONS = {
    '.html', '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg',
    '.webp', '.ico', '.pdf', '.woff', '.woff2', '.ttf', '.json'
}

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    ext = os.path.splitext(path)[1].lower()
    if ext not in ALLOWED_STATIC_EXTENSIONS:
        abort(404)
    return send_from_directory('.', path)

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return '', 200

    # Read Groq API key from environment variable
    groq_api_key = os.environ.get('GROQ_API_KEY')
    if not groq_api_key:
        return jsonify({'error': {'message': 'GROQ_API_KEY not configured on server.'}}), 500

    # Read request body
    input_data = request.get_json()
    if not input_data or 'messages' not in input_data or not isinstance(input_data['messages'], list):
        return jsonify({'error': {'message': 'Missing messages array in request body.'}}), 400

    # Call Groq API
    payload = {
        'model': 'openai/gpt-oss-120b',
        'messages': input_data['messages'],
        'temperature': 0.7,
        'max_tokens': 512
    }

    try:
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            json=payload,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {groq_api_key}'
            },
            timeout=30
        )
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': {'message': f'Failed to connect to Groq API: {str(e)}'}}), 502

if __name__ == '__main__':
    app.run()
