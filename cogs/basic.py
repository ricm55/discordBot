#here are the basics stuff for the bot
import discord
from discord.ext import commands, tasks
import json
from itertools import cycle
import random

with open("json/gameList.json") as f:
    gameList = json.load(f)

with open("json/answer.json") as f:
    answer = json.load(f)

class Basic(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.game = cycle(gameList)
        self.change_status.start()
    
    #--------------------- basic tasks ------------------------------
    @tasks.loop(minutes=2.0)
    async def change_status(self):
        await self.bot.wait_until_ready()

        await self.bot.change_presence(activity=discord.Game(next(self.game)))
    
    #--------------------- basic events ------------------------------
    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot is ready as {0.user}'.format(self.bot))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        #get the new gamer server
        guild = self.bot.get_guild(member.guild.id)
        #write message in general chat (the first text channel in the discord)
        channel = guild.get_channel(member.guild.text_channels[0].id)
        await channel.send(f'Welcome to the server {member.mention} ! :partying_face:')
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):

        #get the server of the new gamer
        guild = self.bot.get_guild(member.guild.id)
        #write message in general chat (the first text channel in the discord)
        channel = guild.get_channel(member.guild.text_channels[0].id)
        await channel.send(f'Good bye {member.mention}, we will miss you... :cry::cry::cry:')

    @commands.Cog.listener()
    async def on_command_error(self,ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("one or more arguments are missing bro")

        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Wut??? I don't know this command, sorry :cry:")

    #--------------------- basic commands ------------------------------
    #Send user latency
    @commands.command()
    async def ping(self, ctx):
        await ctx.send("{} {}ms".format(ctx.author.mention,round(self.bot.latency * 1000,2)))

    #Can repeat what the user wrote
    @commands.command()
    async def repeat(self, ctx, *, arg):
        await ctx.send(arg)

    #Send the user Id
    @commands.command()
    async def getid(self, ctx):
        await ctx.send("your id: {}".format(ctx.author.id) )

    #Send random answer
    @commands.command()
    async def question(self, ctx,message):
        await ctx.send(random.choice(answer))

    #join the channel
    @commands.command()
    async def join(self, ctx):
        channel = ctx.message.author.voice.channel
        await channel.connect()

    #leave the channel
    @commands.command()
    async def leave(self, ctx):
        print("leave the channel")
        await ctx.voice_client.disconnect()

def setup(bot):
   bot.add_cog(Basic(bot))