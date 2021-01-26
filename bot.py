#this is a discord bot for real gamer

import discord
from discord.ext import commands, tasks

from itertools import cycle
import random
import json

#allow bot to track members
intents = discord.Intents.default()
intents.members = True

#load json files, i know i'm smart
with open("json/config.json") as f:
    config = json.load(f)

with open("json/answer.json") as f:
    answer = json.load(f)

with open("json/gameList.json") as f:
    gameList = json.load(f)

bot = commands.Bot(command_prefix=config["prefix"],intents=intents)

#externe modules
extensions = ['cogs.youPlay','cogs.twitchNotif']

if __name__ == '__main__':
    for ex in extensions:
        bot.load_extension(ex)

game = cycle(gameList)

#--------------------- basic tasks ------------------------------

#Can change bot status each 2 minutes
@tasks.loop(minutes = 2.0)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(game)))

#--------------------- basic events ------------------------------
@bot.event
async def on_ready():
    print('Bot is ready as {0.user}'.format(bot))
    change_status.start()
    #twitch_notif.start()

@bot.event
async def on_member_join(member):
    
    #get the new gamer server
    guild = bot.get_guild(member.guild.id)

    #write message in general chat (the first text channel in the discord)
    channel = guild.get_channel(member.guild.text_channels[0].id)

    await channel.send(f'Welcome to the server {member.mention} ! :partying_face:')

@bot.event
async def on_member_remove(member):

    #get the server of the new gamer
    guild = bot.get_guild(member.guild.id)

    #write message in general chat (the first text channel in the discord)
    channel = guild.get_channel(member.guild.text_channels[0].id)
    
    await channel.send(f'Good bye {member.mention}, we will miss you... :cry::cry::cry:')

#handles commands errors
@bot.event
async def on_command_error(ctx, error):
    
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("one or more arguments are missing bro")

    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Wut??? I don't know this command, sorry :(")
#--------------------- basic commands ------------------------------
 
#Send user latency
@bot.command()
async def ping(ctx):
    await ctx.send("{} {}ms".format(ctx.author.mention,round(bot.latency * 1000,2)))

#Can repeat what the user wrote
@bot.command()
async def repeat(ctx, *, arg):
    await ctx.send(arg)

#Send the user Id
@bot.command()
async def getid(ctx):
    await ctx.send("your id: {}".format(ctx.author.id) )

#Send random answer
@bot.command()
async def question(ctx,message):
    await ctx.send(random.choice(answer))

#join the channel
@bot.command()
async def join(ctx):

    channel = ctx.message.author.voice.channel
    await channel.connect()

#leave the channel
@bot.command()
async def leave(ctx):
    print("leave the channel")
    await ctx.voice_client.disconnect()

#--------------------- run ------------------------------

bot.run(config["token"])


