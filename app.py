import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
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
        'model': 'llama-3.3-70b-versatile',
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

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run()
