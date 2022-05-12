import requests
from dotenv import load_dotenv
import os
from validators.url import url
import youtube_dl
from youtubesearchpython import VideosSearch
import base64
import time



load_dotenv()
SPOTIFY_PLAYLIST_ID = "4HU9MyPSDbjbUk8suzXyxU"


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': False,
    'no_warnings': False,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',
    }]
}
ffmpeg_options = {
    'options': '-vn'
}
  
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

  
def generateSpotifyAccessToken():
    
    s = os.getenv("SPOTIFY_CLIENT_ID") + ":" + os.getenv("SPOTIFY_CLIENT_SECRET")
        
    message_bytes = s.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64Message = base64_bytes.decode('ascii')

    headers = {
        'Content-Type' : 'application/x-www-form-urlencoded' , 
        'Authorization' : "Basic " + base64Message
    }

    data = {
        "grant_type" : "client_credentials"
    }

    response = requests.post('https://accounts.spotify.com/api/token', data=data , headers=headers).json()
    print(response)
    if "error" in response:
        return True , response["error"]
    else:
        return False , response["access_token"]

def _getURLFromSpotifyPlaylist(id):
        
    print("Spotify ID" , id)
    if id == None or len(id) == 0:
        return False

        
    token = os.getenv("SPOTIFY_TOKEN")
    expiry = int(os.getenv("SPOTIFY_TOKEN_TIME"))
    rn = int(time.time())
    print("Token is " , token)
    if token == "" or len(token) < 2 or rn >= expiry:
        print("Running Token IF")
        error , token = generateSpotifyAccessToken()
        if error:
            print(token)
            return []
        os.environ["SPOTIFY_TOKEN"] = token
        os.environ["SPOTIFY_TOKEN_TIME"] = str(int(time.time()) + 3500)
        

    url = f"https://api.spotify.com/v1/playlists/{id}/tracks?fields=items(track(name%2Cartists(name)%2Calbum(name)))&limit=100&offset=200"
    headers = {"Authorization": "Bearer " + token}
    response = requests.get(url , headers=headers).json()

    if "error" in response:
        print("Spotify Error" , response)
        return []

    print("Response is" , response)
    songsNotFound = ""
    songs = []
    for track in response["items"]:
        artist = ""
        if(len(track["track"]["artists"]) != 0):
            artist = track["track"]["artists"][0]["name"]
            
        query = track["track"]["name"] + " " + artist
            
        songs.append({ "url" : "url" , "title" : query })
    return songs



songs = _getURLFromSpotifyPlaylist(SPOTIFY_PLAYLIST_ID)
# print(songs)
# for song in songs:
#     res = VideosSearch(song["title"] , 1).result()["result"]
#     if len(res) == 0:
#         print("No Video Found for " , song["title"])
#     else:
#         print("*" * 50 , "Downloading " + song["title"] , "*" * 50 )
#         ytdl.extract_info(res[0]["link"] , download=True)    
#         print("*" * 50 , "Downloaded " + song["title"] , "*" * 50 )


#ytdl.extract_info("https://www.youtube.com/watch?v=AwcI8WBhD9k" , download=True) 



  