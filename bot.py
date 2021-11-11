import discord
from discord.ext import commands, ipc
from discord_slash.context import SlashContext
from credsfile import NEBULI, MONGOLINK, CLUSTER, COLLECTION
from discord_slash import SlashCommand
import aiohttp
import io
import pymongo
from pymongo import MongoClient

#dont worry about this, this is just setting up some things for the dashboard
class MyBot(commands.Bot):
    def __init__(self,*args,**kwargs):
        super().__init__(*args, **kwargs)

        self.ipc = ipc.Server(self,secret_key = "nevergonnagiveyouup")



cluster = MongoClient(MONGOLINK)
db = cluster[CLUSTER]
collection = db[COLLECTION]


cogs = [
    'cogs.slash',
    'cogs.eco',
    'cogs.level'
]



bot = MyBot(command_prefix='/', intents=discord.Intents.all(
), allowed_mentions=discord.AllowedMentions(everyone=False))

slash = SlashCommand(bot, sync_commands=True,
                    sync_on_cog_reload=True, delete_from_unused_guilds=True)

bot.remove_command('help')


for extension in cogs:
    try:
        bot.load_extension(extension)
        print(f'I have loaded the extension {extension}')
    except Exception as e:
        print(f'Hey! The extension {extension} failed to load, should probably check that out.')

#dashboard things
@bot.event
async def on_ipc_ready():
    #when the ipc server is ready
    print("IPC server is ready to go.")
    
@bot.event
async def on_ipc_error(self, endpoint, error):
    #when the ipc route shows an error
    print(endpoint, "raised", error)


@bot.ipc.route()
async def get_guild_number(data):
    return len(bot.guilds) #returns len of guilds back to the user

@bot.ipc.route() #TODO: switch this to mongodb
async def get_guild_ids(data):
    final = []
    for guild in bot.guilds:
        final.append(guild.id)
    return final
@bot.ipc.route()
async def get_guild(data):
    guild = bot.get_guild(data.guild_id)
    if guild is None: return None

    guild_data = {
        "name": guild.name,
        "id": guild.id
    }

    return guild_data


    

@ bot.event
async def on_ready():
    print('I am ready, throw me out into the world.')
    print(f'I am {bot.user.name}')
    print(f'My ID is {bot.user.id}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.competing, name='a MarioKart race'))
@ bot.event
async def on_guild_join(guild):
    put = {'guild_id': f'{guild.id}', 'welcome': False, 'welcomeChannel': None, 'welcomeTemplate': None, 'welcomeBackground': None, 'welcomeTextcolor': None, 'goodbye': False, 'goodbyeChannel': None, 'goodbyeTemplate': None, 'goodbyeBackground': None, 'goodbyeTextColor': None, 'botCommandsChannel': None}
    collection.insert_one(put)

@ bot.event
async def on_guild_remove(guild):
    thing_to_remove = {'guild_id': f'{guild.id}'}
    collection.delete_one(thing_to_remove)
    
@ bot.event
async def on_slash_command(ctx):
    doc = collection.find_one({'guild_id': f"{ctx.guild.id}"})

    if doc == None:
        put = {'guild_id': f'{ctx.guild.id}', 'welcome': False, 'welcomeChannel': None, 'welcomeTemplate': None, 'welcomeBackground': None, 'welcomeTextcolor': None, 'goodbye': False, 'goodbyeChannel': None, 'goodbyeTemplate': None, 'goodbyeBackground': None, 'goodbyeTextColor': None, 'botCommandsChannel': None}
        collection.insert_one(put)
        print(f'Attempted to heal {ctx.guild.name}. RESET TO DEFAULT PARAMS')

        doc2 = collection.find_one({'guild_id': f"{ctx.guild.id}"})
        if doc2 == None:
            print(f"Server healing has failed.")
        elif doc2 != None:
            print(f'Successfully healed {ctx.guild.name}. RESET TO DEFAULT PARAMS')
    
    else:
        return


            

@bot.event
async def on_member_join(member):

    doc = collection.find_one({'guild_id': f'{member.guild.id}'})
    welcomeChannel = doc['welcomeChannel']
    welcomeTemplate = doc['welcomeTemplate']
    welcomeBackground = doc['welcomeBackground']
    welcomeTextcolor = doc['welcomeTextcolor']
    welcomestatus = doc['welcome']

    if welcomestatus == True:
        channelid = int(welcomeChannel)
        channel = await bot.fetch_channel(channelid)

        username = member.name
        discriminator = member.discriminator
        guildname = member.guild.name
        guildmembercount = len(member.guild.members)

        async with aiohttp.ClientSession() as welcomeSession:
            async with welcomeSession.get(f'https://some-random-api.ml/welcome/img/{welcomeTemplate}/{welcomeBackground}?type=join&username={username}&discriminator={discriminator}&avatar={member.avatar_url_as(format="png", size=1024)}&guildName={guildname}&memberCount={guildmembercount}&textcolor={welcomeTextcolor}') as image_resp:
                welcomeImage = io.BytesIO(await image_resp.read())

                await welcomeSession.close()
                await channel.send(file=discord.File(welcomeImage, 'welcome.png'))
    else:
        return
@bot.event
async def on_member_remove(member):

    doc = collection.find_one({'guild_id': f'{member.guild.id}'})
    goodbyeChannel = doc['goodbyeChannel']
    goodbyeTemplate = doc['goodbyeTemplate']
    goodbyeBackground = doc['goodbyeBackground']
    goodbyeTextcolor = doc['goodbyeTextColor']
    goodbyestatus = doc['goodbye']

    if goodbyestatus == True:
        channelid = int(goodbyeChannel)
        channel = await bot.fetch_channel(channelid)

        username = member.name
        discriminator = member.discriminator
        guildname = member.guild.name
        guildmembercount = len(member.guild.members)

        async with aiohttp.ClientSession() as goodbyeSession:
            async with goodbyeSession.get(f'https://some-random-api.ml/welcome/img/{goodbyeTemplate}/{goodbyeBackground}?type=leave&username={username}&discriminator={discriminator}&avatar={member.avatar_url_as(format="png", size=1024)}&guildName={guildname}&memberCount={guildmembercount}&textcolor={goodbyeTextcolor}') as image_resp:
                goodbyeImage = io.BytesIO(await image_resp.read())

                await goodbyeSession.close()
                await channel.send(file=discord.File(goodbyeImage, 'goodbye.png'))
    else:
        return

bot.ipc.start()
bot.run(NEBULI)