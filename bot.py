#this is a discord bot for real gamer

import discord
from discord.ext import commands

import json

#allow bot to track members
intents = discord.Intents.default()
intents.members = True

#load json files, i know i'm smart
with open("json/config.json") as f:
   config = json.load(f)

bot = commands.Bot(command_prefix=config["prefix"],intents=intents)

#externe modules
extensions = ['cogs.basic','cogs.youPlay','cogs.twitchNotif']

if __name__ == '__main__':
    for ex in extensions:
        bot.load_extension(ex)

#--------------------- run ------------------------------

bot.run(config["token"])


