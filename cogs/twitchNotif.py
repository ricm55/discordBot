#can notify user for live twitch
from discord.ext import commands, tasks
import json
import requests

with open("json/config.json") as f:
    config = json.load(f)

class TwitchNotif(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.twitch_notif.start()

    @tasks.loop(seconds = 30)
    async def twitch_notif(self):
        
        await self.bot.wait_until_ready()

        print("let's start the analysis")

        notif = await self.getNotif()
        
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
                    
                    #send message to user
                    userNotif = self.bot.get_user(int(identification))
                    await userNotif.send(f"Hey {userNotif.mention}, {user_login} is now live on \
                                        {twitch_url[0]}! Go check it out!")
                    
                    ((notif[identification])[count])[1] = 0
                
        #save the mustNotify data
        await self.writeNotif(notif)
    #get the notification from the notif file
    async def getNotif(self):
        with open("json/notif.json","r") as notifFile:
            notif = json.load(notifFile)
        notifFile.close()
        return notif

    #write the new notifications in the file
    async def writeNotif(self, notif: dict):
        with open("json/notif.json","w") as notifFile:
            json.dump(notif,notifFile,indent=2)
        
        notifFile.close() 

    async def verifyTwitchUrl(self, url):
        if "https://www.twitch.tv/" in url:
            return True
        else:
            return False

    async def hello(self, ctx):
        print("allo")

    @commands.command()
    async def notifyme(self, ctx, url):

        if not await self.verifyTwitchUrl(url):
            await ctx.send("you must enter a twitch url")
            return

        notif = await self.getNotif()

        #get user config if it exists
        user_config = notif.get(str(ctx.author.id))
        if len(user_config) == 5:
            print("user reache url limits")
            await ctx.send("You reache the limits!!! Remove an url before adding a new one!")
            await self.printNotif(ctx)
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
                    
        await self.writeNotif(notif)

    @commands.command()
    async def stopnotifyme(self, ctx, url):
        
        notif = await self.getNotif()
        all_url = notif.get(str(ctx.author.id))

        for url_pack in all_url:
            if url_pack[0] == url:

                all_url.remove(url_pack)
                print(f"remove {url_pack}")
        
        notif[str(ctx.author.id)] = all_url

        await self.writeNotif(notif)

    @commands.command()
    async def printNotif(self, ctx):
    
        notif = await self.getNotif()
        all_url = notif.get(str(ctx.author.id))

        await ctx.send("here are your twitch notifications:\n{}".format(all_url))

def setup(bot):
   bot.add_cog(TwitchNotif(bot))