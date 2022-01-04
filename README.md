# Raphtalia Python Music Bot
Rahptalia is a Discord Music Bot. You can easily download and invite Raphtalia on your server to listen to high quality music with your friends.

Raphtalia can play high quality songs from youtube.
All functionalities are free meaning no need to pay anything to unlock special features.

Feel free to use this code in your own projects aswell. 


Features
- Play songs from youtube
- add songs to queue using a search query, youtube video link , youtube playlist link, spotify track link and spotify playlist link

Requirements 
- FFMPEG https://www.wikihow.com/Install-FFmpeg-on-Windows 
- Python (This bot was created in v3.9.6) https://www.tutorialspoint.com/how-to-install-python-in-windows
- Discord Bot Token https://discordpy.readthedocs.io/en/stable/discord.html
- Spotify API Token (if you want to add songs using spotify playlists) https://developer.spotify.com/documentation/general/guides/authorization/app-settings/


Installation 
- create a .env file in the root directory of the project 

    ```
    DISCORD= # ADD_YOUR_DISCORD_BOT_TOKEN
    SPOTIFY_CLIENT_ID= # ADD_YOUR_SPOTIFY_CLIENT_ID
    SPOTIFY_CLIENT_SECRET= # ADD_YOUR_SPOTIFY_CLIENT_SERECT 
    SPOTIFY_TOKEN_TIME=0
    SPOTIFY_TOKEN= # leave this blank
    ```
 - install required packages using 
    ```
    pip install -r requirements.py
    ```
- run the bot
  ```
  python server.js
  ```
  
Prefix  ``` !! ```

Commands 
```
  clear        
  join      
  jump , j         
  leave , dc     
  loop        
  pause        
  play       
  playNext , skip , s
  playPrevious , prev , previous
  remove , r
  repeat   
  resume       
  reverse      
  showQueue , q
  shuffle
```

I hope you all will like it.
