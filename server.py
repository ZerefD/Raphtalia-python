import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

bot = commands.Bot(command_prefix = "!!")

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD")

GUILD_VC_TIMER = {}

@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == bot.user.id:
        return

    # when before.channel == None that means use has joined a channel and was not in any other channel
    if before.channel != None:
        voice = discord.utils.get(bot.voice_clients , channel__guild__id = before.channel.guild.id)
        if voice == None:
            print("Voice is None")
            return
        
        if voice.channel.id != before.channel.id:
            print("voice and after channelID != " )
            return

        if len(voice.channel.members) <= 1:
            GUILD_VC_TIMER[before.channel.guild.id] = 0
            while True:
                print("Time" , str(GUILD_VC_TIMER[before.channel.guild.id]) , "Total Members" , str(len(voice.channel.members)))
                await asyncio.sleep(1)
                GUILD_VC_TIMER[before.channel.guild.id] += 1
                if len(voice.channel.members) >= 2 or not voice.is_connected():
                    break
                if GUILD_VC_TIMER[before.channel.guild.id] >= 60:
                    await voice.disconnect()
                    return
     
@bot.event
async def on_ready():
    print("Bot is ready")



cog_files = ['modules.general' , 'modules.music']

for cog_file in cog_files: # Cycle through the files in array
    bot.load_extension(cog_file) # Load the file
    print("%s has loaded." % cog_file) # Print a success message.


bot.run(DISCORD_TOKEN)