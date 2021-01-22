#this is a discord bot for real gamer

import discord
from discord.ext import commands, tasks
from discord.utils import get
import youtube_dl

import twitch
import urllib3
import requests

from itertools import cycle
import random
import json
import os

#import cogs
#import youPlay
#from cogs import youPlay

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
extensions = ['cogs.youPlay']

if __name__ == '__main__':
    for ex in extensions:
        bot.load_extension(ex)

game = cycle(gameList)

#---------------- twitch function -----------------
async def getNotif():
    with open("json/notif.json","r") as notifFile:
        notif = json.load(notifFile)
    notifFile.close()
    return notif

async def writeNotif(notif: dict):
    with open("json/notif.json","w") as notifFile:
        json.dump(notif,notifFile,indent=2)
    
    notifFile.close() 

async def verifyTwitchUrl(url):
    if "https://www.twitch.tv/" in url:
        return True
    else:
        return False

#--------------------- task ------------------------------

#Can change bot status each 2 minutes
@tasks.loop(minutes = 2.0)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(game)))

#twitch notification
@tasks.loop(seconds = 30)
async def twitch_notif():
    print("let's start the analysis")

    notif = await getNotif()
    
    print(f"I get the notification file: {notif}")
    for identification in notif.keys():
        print(f"Let's watch the user: {identification}")

        for count, twitch_url in enumerate(notif[str(identification)]):
            print(f"Let's watch the url: {twitch_url}")
            
            #get the access token
            url_oauth = 'https://id.twitch.tv/oauth2/token'
    
            ask_token = {
                'client_id' : config["twitch_client_id"],
                'client_secret' : config["twitch_client_secret"],
                'grant_type' : 'client_credentials'
            }
            print("I will send the request for access token...")
            #get the token for data access
            response_token = requests.post(url_oauth, ask_token)
            data_token = response_token.json()
            token = data_token["access_token"]
            print(f"I receive {data_token}")

            #get if the live user is up
            user_login = twitch_url[0].replace("https://www.twitch.tv/",'')
            authorisation = 'Bearer'+ ' ' + token 
            url_stream = 'https://api.twitch.tv/helix/streams'
            header_stream = {
                'Authorization' : authorisation,
                'Client-Id' :  config["twitch_client_id"],
            }
            query = {
                'user_login' : user_login
            }
            print("I will send the request for user information...")
            response_stream = requests.get(url_stream, query, headers=header_stream)
            isLive = response_stream.json()
            print(f"I receive: {response_stream}")
            if not isLive['data'] :
                print("no live here")
                live = False
                ((notif[identification])[count])[1] = 1
            else:
                print("he is live!!!")
                live = True

            #send a message to the user
            if live == True and ((notif[identification])[count])[1] == 1:
                await bot.get_user(int(identification)).send("LIIIIVE")
                ((notif[identification])[count])[1] = 0
            
    #save the mustNotify data
    await writeNotif(notif)
#--------------------- event ------------------------------

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

@bot.command()
async def notifyme(ctx, url):
    if not await verifyTwitchUrl(url):
        await ctx.send("you must enter a twitch url")
        return
    notif = await getNotif()
    
    #get user config if it exists
    user_config = notif.get(str(ctx.author.id))
    if len(user_config) == 5:
        print("user reache url limits")
        await ctx.send("You reache the limits!!! Remove an url before adding a new one!")
        await printNotif(ctx)
        return

    #verify if user reached url limits
    if user_config == None:
        #new user for notif
        notif[str(ctx.author.id)] = [[url,1]]
    else:
        for u in user_config:
            if u == url:
                print("user try to notify a channel that he has already notified")
                await ctx.send("you are already notify about that channel")
                return
        
        #add config for old user
        user_config.append([url,1])
        notif[str(ctx.author.id)] = user_config
                
    await writeNotif(notif)

@bot.command()
async def stopnotifyme(ctx, url):


    notif = await getNotif()

    all_url = notif.get(str(ctx.author.id))

    for url_pack in all_url:
        if url_pack[0] == url:

            all_url.remove(url_pack)
            print(f"remove {url_pack}")
    
    notif[str(ctx.author.id)] = all_url

    await writeNotif(notif)

@bot.command()
async def printNotif(ctx):
    
    notif = await getNotif()
    all_url = notif.get(str(ctx.author.id))

    await ctx.send("here are your twitch notifications:\n{}".format(all_url))

@bot.command()
async def test(ctx):
    url_user = 'https://www.twitch.tv/echo_locations'
    url_user = url_user.replace("https://www.twitch.tv/",'')

    url_oauth = 'https://id.twitch.tv/oauth2/token'
    
    ask_token = {
        'client_id' : config["twitch_client_id"],
        'client_secret' : config["twitch_client_secret"],
        'grant_type' : 'client_credentials'
    }

    #get the token for data access
    response_token = requests.post(url_oauth,ask_token)
    data_token = response_token.json()
    token = data_token["access_token"]

    authorisation = 'Bearer'+ ' ' + token

    url_stream = 'https://api.twitch.tv/helix/streams'
    
    header_stream = {
        'Authorization' : authorisation,
        'Client-Id' :  config["twitch_client_id"],
    }

    query = {
        'user_login' : url_user
    }

    response_stream = requests.get(url_stream, query, headers=header_stream)
    isLive = response_stream.json()

    if not isLive['data'] :
        print("no live here")
        await ctx.send("no live here")
    else:
        print("he is live!!!")
        await ctx.send("he is live!!!")
    

#--------------------- run ------------------------------

bot.run(config["token"])

"""
Idea:

create modules for twitch and youtube
create rank system
create help command in externe file
modified readme for documentation
Event
RankSystem: a rank is determine by each user depending the number of messages they send
Command:
myRank: Show the user's Rank

**add log system

installation:
linux/mac
python3 -m pip install -U discord.py[voice]
pip install discord.py --upgrade
ffmpeg - <see the command line>
youtube_dl - <see the command line>
twitch - <see the command line>

Windows
py -3 -m pip install -U discord.py[voice]
ffmpeg on the site (put in C: and setup variable environnement )
python -m pip install -U youtube_dl
python -m pip install twitch-python

pas eu a le faire, deja install???
python -m pip install urllib3
"""

