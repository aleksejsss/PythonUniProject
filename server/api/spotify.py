from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json

load_dotenv()

spotify_client_id = os.getenv('SPOTIFY_Client_ID')
spotify_client_secret = os.getenv('SPOTIFY_Client_Secret')

def get_token(): # Funkcija atgriež tokenu kurš nepieciešams spotify web api izmantošanai
    auth_str = spotify_client_id + ":" + spotify_client_secret
    auth_bytes = auth_str.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    url = 'https://accounts.spotify.com/api/token'
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {'grant_type': 'client_credentials'}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token): # Formatē tokenu vieglākai izmantošanai
    return {'Authorization': 'Bearer ' + token}

def get_objectt_id(token, object_type, title):
    url = 'https://api.spotify.com/v1/search'
    headers = get_auth_header(token)
    query = f'q={title}&type={object_type}&limit=1'
    
    query_url = url + '?' + query
    
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)[f'{object_type}s']['items']
    
    if len(json_result) != 0:
        return json_result[0]
    else:
        print(f'No {object_type} with the name "{title}" was found')
        return None
    
token = get_token()

test_artist = get_objectt_id(token, 'artist', 'Мумий троль')




