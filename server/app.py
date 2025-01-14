from flask import Flask, redirect, request, jsonify
from flask_socketio import SocketIO, emit
import os
import requests as rq
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URL = 'http://localhost:5020/callback'

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return 'Welcome to the app! <a href="/login">Login with Spotify</a>'

@app.route('/login')
def login():
    scope = 'user-read-private user-read-email'
    params = {
        'client_id': SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URL,
        'show_dialog': True
    }
    auth_url = f'{AUTH_URL}?{urllib.parse.urlencode(params)}'
    return redirect(auth_url)

@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({'error': request.args['error']})

    if 'code' in request.args:
        code = request.args.get('code')
        print(f"Authorization code received: {code}")
        
        req_body = {
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URL,
            'client_id': SPOTIFY_CLIENT_ID,
            'client_secret': SPOTIFY_CLIENT_SECRET
        }

        print(f"Request body for token exchange: {req_body}")
        
        try:
            response = rq.post(TOKEN_URL, data=req_body)

            # Debugging: Print the response status and content
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.text}")

            if response.status_code != 200:
                return jsonify({'error': 'Failed to retrieve token', 'details': response.text}), response.status_code

            token_info = response.json()
            print(f"Token Info: {token_info}")

            # Emit the token to the client using WebSocket
            socketio.emit('token_info', token_info, broadcast=True)

            return jsonify({'message': 'Token sent to client'}), 200

        except Exception as e:
            print(f"Error during token exchange: {e}")
            return jsonify({'error': 'Failed to retrieve token', 'details': str(e)}), 500

    return jsonify({'error': 'Authorization code missing'}), 400

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5020, debug=True)
