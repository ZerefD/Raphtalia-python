from discord.ext import commands


class General(commands.Cog):

    def __init__(self , client):
        self.client = client

    @commands.command()
    async def greet(self , ctx):
        await ctx.send("Hello Discord!")

def setup(client):
    client.add_cog(General(client))
