#this is a discord bot for real gamer

import discord
from discord.ext import commands, tasks
from discord.utils import get
import youtube_dl
from itertools import cycle
import random
import json
import os

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

game = cycle(gameList)

#--------------------- task ------------------------------

#Can change bot status each 2 minutes
@tasks.loop(minutes = 2.0)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(game)))

#--------------------- event ------------------------------

@bot.event
async def on_ready():
    print('Bot is ready as {0.user}'.format(bot))
    change_status.start()

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
#--------------------- command ------------------------------

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
async def getId(ctx):
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


#play music with youtube video
@bot.command()
async def play(ctx,url):

    await join(ctx)

    voice = get(bot.voice_clients,guild=ctx.guild)

    #if music is already playing
    if not voice.is_playing():

        #delete old song
        song_there = os.path.isfile("song.mp3")
        try:
            if song_there:
                os.remove("song.mp3")
                print("Removed old song file")
        except PermissionError:
            print("Trying to delete everything ready now")
            await ctx.send("ERROR: Music playing")
            return
        
        voice = get(bot.voice_clients, guild=ctx.guild)

        ydl_opts = {
            "format":"bestaudio/best",
            "postprocessors": [{
                "key":"FFmpegExtractAudio",
                "preferredcodec" : "mp3",
                "preferredquality":"192",
            }],
        }

        #download the video
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("Downloading audio now")
            ydl.download([url])

        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                name = file
                print(f"Renamed File: {file}\n")
                os.rename(file,"song.mp3")
        
        #convert video to audio
        voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: print(f"{name} has finished playing"))
        voice.source = discord.PCMVolumeTransformer(voice.source)
        voice.source.volume = 0.07

        #print the name of the songs in the channel
        new_name = name.rsplit("-",2)
        await ctx.send(f"Playing {new_name[0]}")
        print("playing")
    else:
        await ctx.send(f"A music is already playing")

@bot.command()
async def pause(ctx):
    
    voice = get(bot.voice_clients,guild=ctx.guild)

    #verify if the bot is in a channel and if he is playing music
    if voice and voice.is_playing():
        print("Music paused")
        voice.pause()
        await ctx.send("Music paused")
    else:
        print("Music not playing => failed pause")
        await ctx.send("Music not playing => failed pause")

@bot.command()
async def resume(ctx):
    voice = get(bot.voice_clients,guild=ctx.guild)

    if voice and voice.is_paused():
        print("Resumed music")
        voice.resume()
        await ctx.send("Resumed music")
    else:
        print("Music is not paused")
        await ctx.send("Music is not paused")

@bot.command()
async def stop(ctx):
    voice = get(bot.voice_clients,guild=ctx.guild)

    #verify if the bot is in a channel and if he is playing music
    if voice and voice.is_playing():
        print("Music stopped")
        voice.stop()
        await ctx.send("Music stopped")
        await leave(ctx)
    else:
        print("No music playing => failed to stop")
        await ctx.send("No music playing => failed to stop")
#--------------------- run ------------------------------

bot.run(config["token"])

"""
Idea:

Event
RankSystem: a rank is determine by each user depending the number of messages they send
TwitchNotif: Send notif in private message to all user that want to be notif about twitch live

Command:
myRank: Show the user Rank
NotifMe: Setup twitch channel to notif


installation:
linux/mac
python3 -m pip install -U discord.py[voice]
pip install discord.py --upgrade
ffmpeg - <see the command line>
youtube_dl - <see the command line>
Windows
py -3 -m pip install -U discord.py[voice]
ffmpeg on the site (put in C: and setup variable environnement )
youtube_dl - python -m pip install -U youtube_dl
"""

