from flask import Flask, request, render_template, redirect, url_for
from flask_socketio import SocketIO
import time
from dotenv import load_dotenv
import os
import urllib.parse
import requests

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URL = 'http://localhost:5020/callback'

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'

app = Flask(__name__)
socketio = SocketIO(app)

connected_clients = {}  # Set of active users

"""
{
    sid : <- User session id is used to identify the user
    {
        authorized : bool,
        access_token : access_token,
        refresh_token : refresh_token <- The expires in is a constant 3600, for users that are not autharized skip the token part
    }
}
"""

@socketio.on('connect')
def handle_connect():
    sid = request.sid
    connected_clients[sid] = {'authorized' : False, 'access_token' : '', 'refresh_token' : ''}
    print(f"Client {sid} connected")
    socketio.emit('connect_success', {'message': 'Connection successful', 'assigned_sid' : sid}, to=sid)

@socketio.on('request_authorization')
def handle_authorization(data):
    client_sid = data.get('client_sid')
    if not client_sid:
        print("Received authorization request without client_sid.")
        return

    # Completely reset the session for this client
    if client_sid in connected_clients:
        connected_clients[client_sid] = {'authorized': False, 'access_token': '', 'refresh_token': ''}

    # Proceed with authorization
    scope = 'user-read-private user-read-email playlist-read-private user-top-read'

    params = {
        'client_id': SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URL,
        'show_dialog': True,
        'state': client_sid  # Include client_sid in the state parameter
    }

    auth_url = f'{AUTH_URL}?{urllib.parse.urlencode(params)}'
    response_data = {
        'server_sid': request.sid,
        'auth_url': auth_url
    }

    print(f"Emitting 'authorization_link' to {client_sid}")
    socketio.emit('authorization_link', response_data, to=client_sid)



@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    del connected_clients[sid]
    print(f"Client {sid} disconnected. Remaining connected clients: {connected_clients}")

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code or not state:
        return "Authorization failed. Missing code or state.", 400

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URL,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET
    }

    response = requests.post(TOKEN_URL, data=data)
    if response.status_code != 200:
        return "Authorization failed. Unable to get token.", 400
    
    token_info = response.json()

    sid = state

    if sid in connected_clients:
        connected_clients[sid]['authorized'] = True
        connected_clients[sid]['access_token'] = token_info.get('access_token')
        connected_clients[sid]['refresh_token'] = token_info.get('refresh_token')
        print(f"User {sid} authorized successfully")
    else:
        print(f"Unknown session {sid} attempting to authorize.")
        
    headers = {
    'Authorization': f'Bearer {connected_clients[sid]["access_token"]}'
    }
    
    print(connected_clients[sid])
    
    back_response = requests.get('https://api.spotify.com/v1/me', headers=headers)
    time.sleep(1)
    top_artists_response = requests.get('https://api.spotify.com/v1/me/top/artists?time_range=long_term&limit=50&offset=0', headers=headers)
    time.sleep(1)
    top_tracks_response = requests.get('https://api.spotify.com/v1/me/top/tracks?time_range=long_term&limit=50&offset=0', headers=headers)
    
    if back_response.status_code == 200 and top_artists_response.status_code == 200 and top_tracks_response.status_code == 200:
        personal_data = back_response.json()
        artist_data = top_artists_response.json()
        track_data = top_tracks_response.json()
        socketio.emit('welcome_back', {'user_data': personal_data, 'artist_data': artist_data, 'track_data': track_data}, to=sid)
    else:
        print(f"Error fetching data:\nUser Data: {back_response.status_code}\nTop Artists: {top_artists_response.status_code}\nTop Tracks: {top_tracks_response.status_code}")

        
    return render_template('success.html', token_info=token_info, sid=sid)


if __name__ == '__main__':
    print("Server started...")
    socketio.run(app, debug=True, host='localhost', port=5020)
