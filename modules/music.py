import discord
from discord import guild
from discord.ext import commands
from discord import FFmpegPCMAudio
import youtube_dl
import asyncio
from youtubesearchpython import VideosSearch



async def send(ctx , title = "" , desc = "" , img = ""):
    e = discord.Embed(title = title , description = desc)
    e.set_image(url=img)
    await ctx.send(embed=e)

class Queue():
    def __init__(self):
        self.QUEUE = {}

    def enqueue(self, guildID , url , title , img = ""):
        if guildID not in self.QUEUE:
            self.QUEUE[guildID] = {
                "current" : 0,
                "loop" : False,
                "repeat" : False,
                "queue" : []
            }

        if url == " " or title == " " or len(url) == 0 or len(title) == 0:
            return False

        self.QUEUE[guildID]["queue"].append({
            "url" : url,
            "title" : title,
            "img" : img
        })  

        # print("*" * 100)
        # print("New Queue\n" , self.QUEUE[guildID]["queue"])
        # print("*" * 100)
        return True
        
    def getSong(self , guildID , nextSong = True):
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

        if nextSong:
            newSongIndex += 1
        else:
            newSongIndex -= 1
        
        if newSongIndex < 0:
            newSongIndex = 0

        elif newSongIndex >= queueSize:
            if loop:
                newSongIndex = 0
            else:
                newSongIndex = -1

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

        return "Repeating Song " + str( self.QUEUE[guildID]["repeat"] )


    def printQueue(self , guildID):
        
        if guildID not in self.QUEUE:
            return "Not currently playing anything."
        
        output = ""
        index = 0
        for song in self.QUEUE[guildID]["queue"]:

            output += str((index + 1)) + ") " + song["title"] 
            if self.QUEUE[guildID]["current"] == index:
                output += " **(now playing)** \n"
            else:
                output += "\n"
            index += 1
            
        return output

class MediaPlayer(commands.Cog):

    def __init__(self , client):
        self.client = client
        self.queue = Queue()
        self.ytdl_format_options = {
            'format': 'bestaudio/best',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': False,
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
        if ctx.author.voice.channel == None:
            await send(ctx , desc="You must be in a voice channel to use this command")
            return False

        try:
            voiceClient = await ctx.author.voice.channel.connect()
            await send(ctx , desc="Connected")
            return voiceClient
        except Exception as ex:
            print(ex)
            await send(ctx , desc="Unable to join voice channel " + ctx.author.voice.channel.name + str(ex))
            return False
        

    @commands.command(aliases=["dc" , "disconnect"])
    async def leave(self , ctx):
        if ctx.author.voice.channel == None:
            await send(ctx , desc="You must be in a voice channel to use this command")
            return

        try:
            if len(self.client.voice_clients) == 0:
                await send(ctx , desc="No Active Voice Connections")
                return

            for connection in self.client.voice_clients:
                if ctx.guild.id == connection.channel.guild.id:
                    await connection.disconnect()
                    await send(ctx , desc="Disconnected from " + connection.channel.name)

        except Exception as ex:
            print(ex)
            await send(ctx , desc="Unable to disconnect from the voice channel " + ctx.author.voice.channel.name + str(ex))
    
    async def _youtubeURL(self,url):
        loop = asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(url , download=False))    
            musicURL = data["formats"][3]["url"]
            musicTitle = data["title"]
            return musicURL , musicTitle , False
        except Exception as ex:
            print(ex)
            return False , False , "Something went wrong " + str(ex)

    @commands.command(aliases=["p"])
    async def play(self , ctx , *args , skip = False , musicTitle = "" , musicURL = "" , musicImg = ""):

        if len(args) == 0 and musicURL == "" and musicTitle == "":
            await send(ctx , desc="No URL Provided")
            return
        
        if len(args) == 0:
            url = musicURL
        else:
            query = " ".join(args[:])
            res = VideosSearch(query , 1).result()["result"]
            print(res)
            if len(res) == 0:
                await send(ctx , desc="No Video found")
                return
            url = res[0]["link"]

        voice = None
        for connection in self.client.voice_clients:
            if ctx.guild.id == connection.channel.guild.id:
                voice = connection
                break
        
        if voice == None:
            print("Used join command to connect")
            voice = await self.join(ctx)

        if skip == False:
            musicURL , musicTitle , error = await self._youtubeURL(url)
            if error:
                await send(ctx , desc=error)
                return

            res = self.queue.enqueue(ctx.guild.id , musicURL , musicTitle)
            if not res:
                await send(ctx , desc="Unable to add the given URL" + url)
                return

        isPlaying = voice.is_playing()
        if isPlaying and skip == False:
            await send(ctx , desc="Added " + musicTitle + " to the queue")
            return

        if isPlaying and skip == True:
            voice.stop()
            return

        player = discord.FFmpegPCMAudio(musicURL , **self.ffmpeg_options)
        voice.play(player , after= lambda e: asyncio.run_coroutine_threadsafe(self.playNext(ctx , songIndex=2), self.client.loop))
        await send(ctx , title="Now Playing" , desc= musicTitle , img=musicImg)

   

    @commands.command(aliases=["next" , "skip" , "s"])
    async def playNext(self , ctx , *args , songIndex = 1):
        
        if ctx.author.voice.channel == None:
            await send(ctx , desc="You must be in a voice channel to use this command")
            return

        voice = None
        for connection in self.client.voice_clients:
            if ctx.guild.id == connection.channel.guild.id:
                voice = connection
                break
        if voice == None:
            await send(ctx , desc="VoiceClient is False")
            return

        if voice.is_playing():
            voice.stop()
            return

        song = self.queue.getSong(ctx.guild.id , True)
        print("New Song" , song)
        if song == False:
            if songIndex == 2:
                await send(ctx , desc="Stopping playback. No more songs in the queue.")
            else:
                await send(ctx , desc="No more songs in the queue.")
                
            return

        #await self.play(ctx , musicURL=song["url"] , musicTitle=song["title"] , skip = True)
        player = discord.FFmpegPCMAudio(song["url"] , **self.ffmpeg_options)
        voice.play(player , after= lambda e: asyncio.run_coroutine_threadsafe(self.playNext(ctx , songIndex=2), self.client.loop))
        await send(ctx , title="Now Playing" , desc= song["title"] , img = song["img"])
  
            
    @commands.command(aliases=["previous" , "prev"])
    async def playPrevious(self , ctx , *args , songIndex = 1):
        if ctx.author.voice.channel == None:
            await send(ctx , desc="You must be in a voice channel to use this command")
            return

        song = self.queue.getSong(ctx.guild.id , False)
        print("New Song" , song)
        if song == False:
            await send(ctx , desc="No more songs in the queue.")
            return

        await self.play(ctx , musicURL=song["url"] , musicTitle=song["title"] , img = song["img"] , skip = True)

    @commands.command()
    async def loop(self,  ctx , *args):
        if ctx.author.voice.channel == None:
            await send(ctx , desc="You must be in a voice channel to use this command")
            return

        await send(ctx , desc=self.queue.looping(ctx.guild.id))

    @commands.command()
    async def repeat(self,  ctx , *args):
        if ctx.author.voice.channel == None:
            await send(ctx , desc="You must be in a voice channel to use this command")
            return

        await send(ctx , desc=self.queue.repeat(ctx.guild.id))
        
        
    @commands.command(aliases=["queue" , "q"])
    async def showQueue(self , ctx , url = None):
        data = self.queue.printQueue(ctx.guild.id)
        await send(ctx , title="Queue" , desc=data)

    @commands.command()
    async def clear(self , ctx):
        await send(ctx , desc=self.queue.clearQueue(ctx.guild.id))

def setup(client):
    client.add_cog(MediaPlayer(client))
