import discord
import requests
from discord.ext import commands
from dotenv import load_dotenv , set_key , find_dotenv
import os
import validators
import youtube_dl
import asyncio
from youtubesearchpython import VideosSearch , Playlist
import base64
import time
import random
import DiscordUtils

"""

    When ANY ACTION is UNSUCCESSFUL, function will return False

"""

load_dotenv()
SPOTIFY_TOKEN = os.getenv("SPOTIFY")

async def send(ctx , title = "" , desc = "" , img = "", color = discord.Colour.dark_gold()):
    e = discord.Embed(title = title , description = desc , color=color)
    e.set_image(url=img)
    await ctx.send(embed=e)


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
        return False , response["error"]
    else:
        return True , response["access_token"]

class TRACK():
    def __init__(self, title = "unknown" , url = "@unknownURL" , img = "" , isQuery = False):
        self.title = title
        self.url = url
        self.isQuery = isQuery
        self.img = img
    def __str__(self):
        return self.title
        
class Queue():
    def __init__(self):
        self.QUEUE = {}

    def enqueue(self, guildID , url , title , isQuery = False , img = ""):
        if guildID not in self.QUEUE:
            self.QUEUE[guildID] = {
                "current" : 0,
                "loop" : False,
                "repeat" : False,
                "queue" : []
            }

        if url == " " or title == " " or len(url) == 0 or len(title) == 0:
            return False

        self.QUEUE[guildID]["queue"].append( TRACK(title=title , url=url , img=img , isQuery=isQuery) )
        return True
        

    def dequeue(self , guildID , trackIndex):
        if trackIndex < 0:
            return False, "Index must be greater than 0"
        
        size = self.getQueueSize(guildID)

        if size == False:
            return False , "No Queue Found"
        
        currentSongIndex = self.QUEUE[guildID]["current"]

        if trackIndex >= size:
            return False, "Index must be less than the queue size " + str(size)

        
        if trackIndex < currentSongIndex:
            self.QUEUE[guildID]["current"] -= 1
            

        del self.QUEUE[guildID]["queue"][trackIndex]

        return True , "Success"



    def getQueueSize(self , guildID):
        if guildID not in self.QUEUE:
            return False
        return len(self.QUEUE[guildID]["queue"])
        
    def setNewCurrentSongIndex(self, guildID , trackIndex):
        if trackIndex < 0:
            return False, "Index must be greater than 0"
        
        size = self.getQueueSize(guildID)

        if size == False:
            return False , "No Queue Found"
        
        if trackIndex >= size:
            return False, "Index must be less than the queue size " + str(size)

        self.QUEUE[guildID]["current"] = trackIndex - 1

        return True , "Success"


    def getSong(self , guildID , nextSong = True , trackIndex = -1):
        if guildID not in self.QUEUE:
            return False
        
        currentSongIndex = self.QUEUE[guildID]["current"]
        newSongIndex = currentSongIndex
        loop = self.QUEUE[guildID]["loop"]
        repeat = self.QUEUE[guildID]["repeat"]
        queue = self.QUEUE[guildID]["queue"]
        queueSize = len(queue)

        if queueSize == 0:
            return False

        newSongIndex = newSongIndex + 1 if nextSong else newSongIndex - 1

        if trackIndex != -1:
            newSongIndex = trackIndex

        if newSongIndex < 0:
            newSongIndex = 0

        elif newSongIndex >= queueSize:            
            newSongIndex = 0 if loop else -1

        if repeat:
            newSongIndex = currentSongIndex
        elif newSongIndex == -1:
            return False
        
        self.QUEUE[guildID]["current"] = newSongIndex
        return self.QUEUE[guildID]["queue"][newSongIndex]
        
    def clearQueue(self , guildID):
        if guildID not in self.QUEUE:
            return "Not currently playing anything."

        self.QUEUE[guildID]["current"] = 0
        self.QUEUE[guildID]["queue"] = []

        return "Queue Emptied"
        


    def looping(self, guildID):
        if guildID not in self.QUEUE:
            return "Not currently playing anything."
        
        self.QUEUE[guildID]["loop"] = not self.QUEUE[guildID]["loop"]

        return "Queue Looping " + str( self.QUEUE[guildID]["loop"] )
    
    def repeat(self, guildID):
        if guildID not in self.QUEUE:
            return "Not currently playing anything."
        
        self.QUEUE[guildID]["repeat"] = not self.QUEUE[guildID]["repeat"]

        return "Repeating Track " + str( self.QUEUE[guildID]["repeat"] )


    def shuffle(self , guildID):
        
        if guildID not in self.QUEUE:
            return False
        
        queue = self.QUEUE[guildID]["queue"]
        currentSongIndex = self.QUEUE[guildID]["current"]

        currentTrack = queue[currentSongIndex]
        del queue[currentSongIndex]

        random.shuffle(queue)
        queue.insert(0 , currentTrack)
        self.QUEUE[guildID]["queue"] = queue
        self.QUEUE[guildID]["current"] = 0

        return True

    def reverse(self , guildID):
        
        if guildID not in self.QUEUE:
            return False
        
        queue = self.QUEUE[guildID]["queue"]
        currentSongIndex = self.QUEUE[guildID]["current"]

        currentTrack = queue[currentSongIndex]
        del queue[currentSongIndex]

        queue.reverse()
        queue.insert(0 , currentTrack)
        self.QUEUE[guildID]["queue"] = queue
        self.QUEUE[guildID]["current"] = 0

        return True


    def printQueue(self , guildID):
        
        if guildID not in self.QUEUE:
            return [ discord.Embed(title="Queue" , description = "Not currently playing anything.") ]
        
        output = ""
        index = 0
        embeds = []
        for track in self.QUEUE[guildID]["queue"]:
            if self.QUEUE[guildID]["current"] == index:
                output += "**" + str((index + 1)) + ") " + track.title + "**\n"
            else:
                output += str((index + 1)) + ") " + track.title + "\n"
            
            index += 1
            if index % 20 == 0:
                embeds.append(
                    discord.Embed(title="Queue" , description = output)
                )
                output = ""

        embeds.append(
            discord.Embed(title="Queue" , description = output)
        )
        if len(embeds) == 0:
            return [ discord.Embed(title="Queue" , description = "Queue is empty.") ]

        return embeds









class MediaPlayer(commands.Cog):

    def __init__(self , client):
        self.client = client
        self.queue = Queue()
        self.ytdl_format_options = {
            'format': 'bestaudio/best',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': False,
            'sleep-interval': 10,
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': False,
            'default_search': 'auto',
            'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
        }
        self.ffmpeg_options = {
            'options': '-vn'
        }

        self.ytdl = youtube_dl.YoutubeDL(self.ytdl_format_options)


    @commands.command()
    async def join(self , ctx):
        if not (await self.checker(ctx)):
            return False

        try:
            voiceClient = await ctx.author.voice.channel.connect()
            return voiceClient
        except Exception as ex:
            print(ex)
            await send(ctx , desc="Unable to join voice channel " + ctx.author.voice.channel.name + str(ex) , color=discord.Colour.red())
            return False
        

    @commands.command(aliases=["dc" , "disconnect"])
    async def leave(self , ctx):
        if not (await self.checker(ctx)):
            return False

        try:
            if len(self.client.voice_clients) == 0:
                await send(ctx , desc="No Active Voice Connections" , color=discord.Colour.red())
                return False

            for connection in self.client.voice_clients:
                if ctx.guild.id == connection.channel.guild.id:
                    await connection.disconnect()
                    await send(ctx , desc="Disconnected from " + connection.channel.name , color=discord.Colour.green())

        except Exception as ex:
            print(ex)
            await send(ctx , desc="Unable to disconnect from the voice channel " + ctx.author.voice.channel.name + str(ex) , color=discord.Colour.red())

    async def _downloadYoutubeVideo(self,tracks):
        loop = asyncio.get_event_loop()
        try:
            returnTracks = []
            for track in tracks:
                data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(track.url , download=False))
                
                if "formats" in data:
                    returnTracks.append( TRACK(title=data["title"] , url=data["formats"][3]["url"]) )

                elif data["_type"] == "playlist":
                    for entries in data["entries"]:
                        returnTracks.append( TRACK(title=entries["title"] , url=entries["formats"][3]["url"]) )
                        
            return returnTracks , True
        except Exception as ex:
            print(ex)
            return str(ex) , False
    
    async def _addSongsToQueue(self, ctx , voice , tracks):
        failedSongs = ""
        successSongs = ""
        anySuccess = False
        firstRun = True
        returnTrack = TRACK()
        totalInserted = 0
        for track in tracks:
            res = self.queue.enqueue(ctx.guild.id , track.url , track.title , isQuery=track.isQuery)
            if not res:
                failedSongs += track.url + "\n"
            else:
                successSongs += track.title + "\n"
                anySuccess = True
                totalInserted += 1
                if firstRun:
                    firstRun = False
                    returnTrack = TRACK(title=track.title , url=track.url , isQuery=track.isQuery , img="")
 
        if failedSongs != "":
            await send(ctx , title="Unable to add the given URLs" , desc=failedSongs , color=discord.Colour.red())
            if not anySuccess:
                return returnTrack , False


        await send(ctx , title = "Added " + str(totalInserted) + " track(s) to queue.", color=discord.Colour.green())
        if voice.is_playing():
            return returnTrack , False

        return returnTrack , True

    @commands.command(aliases=["p"])
    async def play(self , ctx , *args , musicImg = ""):

         # if no arguments are provided return an error
        if len(args) == 0:
            await send(ctx , desc="No URL Provided" , color=discord.Colour.red())
            return
        
        # checking if bot is connected to a VC or not
        voice = discord.utils.get(self.client.voice_clients , channel__guild__id = ctx.guild.id)
        # if bot is not connected to a VC ? then try to join the VC user is in
        if voice == None:
            print("Used join command to connect")
            voice = await self.join(ctx)
            if voice == False: return

        query = " ".join(args[:])
        # if its a url ? then check if its a spotify url or youtube url
        if validators.url(query):
            if "spotify" in query:  
                # returns array of SONGS object [ {"title" , "url"} ] where URL = youtube url
                id = query.split("/")[-1].split("?")[0]
                singleTrack = True if "track" in query else False
                tracks = await self._getURLFromSpotifyPlaylist( id , singleTrack=singleTrack )                 

            else: # its a youtube url  

                # its a video
                if "watch?v=" in query:
                    if "list=" in query:
                        query = query.split("list=")[0]
                        
                    tracks , success = await self._downloadYoutubeVideo([ TRACK(url=query) ])
                    if not success:
                        await send(ctx , title="Invalid URL" , desc=query , color=discord.Colour.red())
                        return False
                    tracks[0].url = query
                # its a playlsit
                elif "list=" in query:
                    # its youtube playlist 
                    tracks,  success , errorMessage = success = await self._getURLFromYTPlaylist(query.split("list=")[1])
                    if not success:
                        await send(ctx , title=errorMessage)
                        return

                # invalid url
                else:
                    await send(ctx , title="Invalid URL" , desc=query , color=discord.Colour.red())
                    return False
            await send(ctx , desc="URL Provided")
        else:
            # if its a search query search youtube.
            tracks = await self._getYoutubeURLFromQueries(ctx,[query])
        
        currentTrack , success = await self._addSongsToQueue(ctx , voice , tracks)
        if not success: return
 
        # print("Provided URL" , urls)
        print("Current Track" , currentTrack)
        if ((currentTrack.title == "" or currentTrack.url == "@unknownURL") and currentTrack.isQuery == False):
            print("Current Track")
            return

        if currentTrack.isQuery:
            currentTrack = (await self._getYoutubeURLFromQueries(ctx , [currentTrack.title]))[0]

        tracks , success = await self._downloadYoutubeVideo([currentTrack])
        
        if not success:
            # here tracks contain error message
            await send(ctx , title="Invalid URL" , desc=tracks , color=discord.Colour.red())
            return False

        if len(tracks) == 0:
            print("SONGS LENGTH IS ZERO")
            return False
        currentTrack = tracks[0]
        
        #t1 = threading.Thread(target=self._downloadYoutubeVideo, args=(url[1:],))
        # add all the tracks to the queue
        
        player = discord.FFmpegPCMAudio(currentTrack.url , **self.ffmpeg_options)
        voice.play(player , after= lambda e: asyncio.run_coroutine_threadsafe(self.playNext(ctx , trackIndex=-1 , someError=e), self.client.loop))
        await send(ctx , title="Now Playing" , desc= currentTrack.title , img=currentTrack.img , color=discord.Colour.green())

    async def _getYoutubeURLFromQueries(self, ctx , queries , isThread = False):
        tracks = []
        for query in queries:
            # if its a search query search youtube.
            # if not isThread:
            #     await send(ctx , desc="Search Query Provided")
            
            res = VideosSearch(query , 1).result()["result"]                
            if len(res) == 0: 
                if not isThread:
                    await send(ctx , desc="No Video found for the query " + query , color=discord.Colour.red())
                else:
                    print("No Video found for the query" , query)
                continue
            tracks.append( TRACK(title=res[0]["title"] , url=res[0]["link"]) )

        return tracks


    async def _getURLFromYTPlaylist(self, id):
        url = "https://www.youtube.com/playlist?list=" + id
        
        
        tracks = []
        try:
            videos = Playlist.getVideos(url)
            for video in videos["videos"]:
                videoLink = video["link"].split("list=")[0]
                tracks.append( TRACK(title=video["title"] , url=videoLink) )

        except Exception as ex:
            return tracks , False , "Invvalid Playlist URL"
        
        return tracks , True , ""



    async def _getURLFromSpotifyPlaylist(self, id , singleTrack=False):
        
        print("Spotify ID" , id)
        if id == None or len(id) == 0:
            return False
        
        token = os.getenv("SPOTIFY_TOKEN")
        expiry = int(os.getenv("SPOTIFY_TOKEN_TIME"))
        rn = int(time.time())
        print("Token is" , token)
        if token == "" or len(token) < 2 or rn >= expiry:
            error , token = generateSpotifyAccessToken()
            if not error:
                print("Spotfy Error" , token)
                return []
            print("New Token is" , token)
            evnFile = find_dotenv()
            os.environ["SPOTIFY_TOKEN"] = token
            os.environ["SPOTIFY_TOKEN_TIME"] = str(int(time.time()) + 3500)
            set_key(evnFile , "SPOTIFY_TOKEN" , os.environ["SPOTIFY_TOKEN"])
            set_key(evnFile , "SPOTIFY_TOKEN_TIME" , os.environ["SPOTIFY_TOKEN_TIME"])
        
        
        
        if singleTrack: 
            url = f"https://api.spotify.com/v1/tracks/{id}"
        else:
            url = f"https://api.spotify.com/v1/playlists/{id}/tracks?fields=items(track(name%2Cartists(name)%2Calbum(name)))&limit=100&offset=0"

        headers = {"Authorization": "Bearer " + token}
        response = requests.get(url , headers=headers).json()

        if "error" in response:
            print("Spotify Error" , response)
            return []

        tracks = []
        if singleTrack:
            artist = ""
            if(len(response["artists"]) != 0):
                artist = response["artists"][0]["name"]

            query = response["name"] + " " + artist
            tracks.append( TRACK(title=query , isQuery=True) )
        else:
            for track in response["items"]:
                artist = ""
                if(len(track["track"]["artists"]) != 0):
                    artist = track["track"]["artists"][0]["name"]
                
                query = track["track"]["name"] + " " + artist
        
                tracks.append( TRACK(title=query , isQuery=True) )

        return tracks

    @commands.command(aliases=["next" , "skip" , "s"])
    async def playNext(self , ctx , *args , trackIndex = -1 , someError = False):
        if someError != False and someError != None:
            print("Printing Some error for voice.play()" , someError)
        
        
        voice = await self.getVoiceClient(ctx)
        if not voice:
            return

        if voice.is_playing():
            voice.stop()
            return

        if self.queue.getQueueSize(ctx.guild.id) == 0:
            await send(ctx , desc="Stopping Playback")
            return

        track = self.queue.getSong(ctx.guild.id , True , trackIndex)
        print("New Track" , track)
        if track == False:
            await send(ctx , desc="Stopping playback. No more songs in the queue.")
            return

        
        if track.isQuery:
            track = (await self._getYoutubeURLFromQueries(ctx , [track.title]))[0]
        tracks , success = await self._downloadYoutubeVideo([track])
        
        if not success:
            # here tracks contain error message
            await send(ctx , title="Invalid URL" , desc=tracks , color=discord.Colour.red())
            return False

        if len(tracks) == 0:
            print("SONGS LENGTH IS ZERO")
            return False
        track = tracks[0]

        
        player = discord.FFmpegPCMAudio(track.url , **self.ffmpeg_options)
        voice.play(player , after= lambda e: asyncio.run_coroutine_threadsafe(self.playNext(ctx , trackIndex=-1 , someError = e), self.client.loop))
        await send(ctx , title="Now Playing" , desc= track.title , img = track.img , color=discord.Colour.green())
  
    
    @commands.command()
    async def pause(self, ctx):
        
        if not (await self.checker(ctx)):
            return
        
        voice = await self.getVoiceClient(ctx)
        if not voice:
            return
        
        if voice.is_playing():
            voice.pause()
            await send(ctx , desc="Player Paused")


    @commands.command()
    async def resume(self, ctx):
        
        if not (await self.checker(ctx)):
            return
        
        
        voice = await self.getVoiceClient(ctx)
        if not voice:
            return
        
        if voice.is_paused():
            voice.resume()
            await send(ctx , desc="Player Resumed")
        
    @commands.command(aliases=["previous" , "prev"])
    async def playPrevious(self , ctx , *args , trackIndex = 1):
        if not (await self.checker(ctx)):
            return

        track = self.queue.getSong(ctx.guild.id , False)
        print("New Track" , track)
        if track == False:
            await send(ctx , desc="No more songs in the queue.")
            return

    @commands.command()
    async def reverse(self , ctx):
        response = self.queue.reverse(ctx.guild.id)
        if response:
            await send(ctx , "Reverse Success")
            return
        await send(ctx , "Something went wrong" , color=discord.Colour.red())

    @commands.command()
    async def shuffle(self , ctx):
        response = self.queue.shuffle(ctx.guild.id)
        if response:
            await send(ctx , "Shuffle Success")
            return
        await send(ctx , "Something went wrong" , color=discord.Colour.red())
    # TODO this functions raises an exception when string is provided as an argument 

    @commands.command(aliases=["r"])
    async def remove(self , ctx , index = -1):
        try:
            index = str(index)
            if index.isdigit() == True:
                index = int(index) - 1
                if index < 0:
                    await send(ctx , desc="Index must be a positive number" , color=discord.Colour.red())
                    return
                if index >= self.queue.getQueueSize(ctx.guild.id):
                    await send(ctx , desc="Index must be a less than the queue size" , color=discord.Colour.red())
                    return
                
                success , errorMessage = self.queue.dequeue(ctx.guild.id , index)
                if not success:
                    print(errorMessage)
                    await send(ctx , desc=errorMessage)
                    return
                else:
                    await send(ctx , desc="Removed the song from index " + str(index + 1))

            else:
                await send(ctx , desc="Index must be an integer and a positive number" , color=discord.Colour.red())
        except Exception as ex:
            print(ex)
            await send(ctx , desc="Index must be an integer" , color=discord.Colour.red())


    @commands.command(aliases=["j"])
    async def jump(self, ctx , index = -1):
        try:
            index = str(index)
            if index.isdigit() == True:
                index = int(index) - 1
                if index < 0:
                    await send(ctx , desc="Index must be a positive number" , color=discord.Colour.red())
                    return
                if index >= self.queue.getQueueSize(ctx.guild.id):
                    await send(ctx , desc="Index must be a less than the queue size" , color=discord.Colour.red())
                    return
                
                success , errorMessage = self.queue.setNewCurrentSongIndex(ctx.guild.id , index)
                if not success:
                    print(errorMessage)
                    await send(ctx , desc=errorMessage , color=discord.Colour.red())
                    return
                await self.playNext(ctx)

            else:
                await send(ctx , desc="Index must be an integer and a positive number" , color=discord.Colour.red())
        except Exception as ex:
            print(ex)
            await send(ctx , desc="Index must be an integer" , color=discord.Colour.red())

    
    @commands.command()
    async def loop(self,  ctx , *args):
        if not (await self.checker(ctx)):
            return

        await send(ctx , desc=self.queue.looping(ctx.guild.id))

    @commands.command()
    async def repeat(self,  ctx , *args):
        if not (await self.checker(ctx)):
            return

        await send(ctx , desc=self.queue.repeat(ctx.guild.id))
        
        
    @commands.command(aliases=["queue" , "q"])
    async def showQueue(self , ctx):
        data = self.queue.printQueue(ctx.guild.id)
        
        paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx)
        paginator.add_reaction('⏮️', "first")
        paginator.add_reaction('⏪', "back")
        paginator.add_reaction('🔐', "lock")
        paginator.add_reaction('⏩', "next")
        paginator.add_reaction('⏭️', "last")
        await paginator.run(data)

    async def checker(self, ctx , checkIfUserInVC = True):
        if ctx.author.voice == None and checkIfUserInVC:
            await send(ctx , desc="You must be in a voice channel to use this command" , color=discord.Colour.red())
            return False
        return True

    async def getVoiceClient(self, ctx):
        voice = discord.utils.get(self.client.voice_clients , channel__guild__id = ctx.guild.id)
        
        if voice == None:
            await send(ctx , desc="VoiceClient is False" , color=discord.Colour.red())
            return False
        return voice

    @commands.command()
    async def clear(self , ctx):
        
        if not (await self.checker(ctx)):
            return

        voice = await self.getVoiceClient(ctx)
        if not voice:
            return
        
        self.queue.clearQueue(ctx.guild.id)
        await self.playNext(ctx)

    
    @commands.command()
    async def paginate(self, ctx):
        embedOne = discord.Embed(
            title = "Page #1", #Any title will do
            description = "This is page one!" #Any description will be fine
        )
        embedTwo = discord.Embed(
            title = "Page #2",
            description = "This is page two!"
        )
        embedThree = discord.Embed(
            title = "Page #3",
            description = "This is page three!"
        )
        paginationList = [embedOne, embedTwo, embedThree]
        current = 0
        paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx)
        paginator.add_reaction('⏮️', "first")
        paginator.add_reaction('⏪', "back")
        paginator.add_reaction('🔐', "lock")
        paginator.add_reaction('⏩', "next")
        paginator.add_reaction('⏭️', "last")
        await paginator.run(paginationList)


def setup(client):
    client.add_cog(MediaPlayer(client))
