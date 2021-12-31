import discord
from discord.ext import commands


bot = commands.Bot(command_prefix = "!!")


@bot.event
async def on_ready():
    print("Bot is ready")



cog_files = ['modules.general' , 'modules.music']

for cog_file in cog_files: # Cycle through the files in array
    bot.load_extension(cog_file) # Load the file
    print("%s has loaded." % cog_file) # Print a success message.


bot.run("NTE5NzIxMDExNjIxNTI3NTYy.XAdJ6Q.9Zz8R4FW6WshKGIvc5rHHwwYuug")