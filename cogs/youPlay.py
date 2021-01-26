#can play music from youtube
import os
import discord
import youtube_dl
from discord.ext import commands
from discord.utils import get


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def play(self, ctx, url):
        #bot joins channel
        channel = ctx.message.author.voice.channel
        await channel.connect()

        voice = get(self.bot.voice_clients,guild=ctx.guild)

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
            
            voice = get(self.bot.voice_clients, guild=ctx.guild)

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

    @commands.command()
    async def pause(self, ctx):
        
        voice = get(self.bot.voice_clients,guild=ctx.guild)

        #verify if the bot is in a channel and if he is playing music
        if voice and voice.is_playing():
            print("Music paused")
            voice.pause()
            await ctx.send("Music paused")
        else:
            print("Music not playing => failed pause")
            await ctx.send("Music not playing => failed pause")
    @commands.command()
    async def resume(self, ctx):
        voice = get(self.bot.voice_clients,guild=ctx.guild)

        if voice and voice.is_paused():
            print("Resumed music")
            voice.resume()
            await ctx.send("Resumed music")
        else:
            print("Music is not paused")
            await ctx.send("Music is not paused")

    @commands.command()
    async def stop(self, ctx):

        voice = get(self.bot.voice_clients,guild=ctx.guild)
        #verify if the bot is in a channel and if he is playing music
        if voice and voice.is_playing():
            print("Music stopped")
            voice.stop()
            await ctx.send("Music stopped")
            await ctx.voice_client.disconnect()
        else:
            print("No music playing => failed to stop")
            await ctx.send("No music playing => failed to stop")

def setup(bot):
    bot.add_cog(Music(bot))