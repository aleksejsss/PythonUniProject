from flask import Flask, redirect, request, jsonify, session, render_template
from flask_socketio import SocketIO, emit
import os
import requests as rq
import urllib.parse
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URL = 'http://localhost:5020/callback'

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET')
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

    # Open the link in the user's default browser
    return redirect(auth_url)

@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({'error': request.args['error']})
    
    if 'code' in request.args:
        # Exchange the authorization code for an access token
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URL,
            'client_id': SPOTIFY_CLIENT_ID,
            'client_secret': SPOTIFY_CLIENT_SECRET
        }
    
        response = rq.post(TOKEN_URL, data=req_body)
        token_info = response.json()
    
        # Store the tokens in the session
        session['token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
    
        # Fetch user profile data from Spotify API
        headers = {
            'Authorization': f'Bearer {session["token"]}'
        }
        user_response = rq.get(API_BASE_URL + 'me', headers=headers)
        user_data = user_response.json()

        # Send the user data to the client via SocketIO
        socketio.emit('user_data', {'user': user_data})
    
        # Render a page informing the user they can return to the app
        return render_template('success.html')


@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': SPOTIFY_CLIENT_ID,
            'client_secret': SPOTIFY_CLIENT_SECRET
        }
        
        response = rq.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()
    
        session['token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']
        
        return redirect('/playlists')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5020, debug=True)
