import discord
from discord_slash import SlashCommand
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils import manage_commands
from discord_slash.model import SlashCommandOptionType
from credsfile import NEBULI, guildids, MONGOLINK, CLUSTER, COLLECTION
from discord.ext.commands.core import has_permissions
import datetime, time
import asyncio
import aiohttp
import factful
import io
import random
import typing

import pymongo
from pymongo import MongoClient

cluster = MongoClient(MONGOLINK)
db = cluster[CLUSTER]
collection = db[COLLECTION]




class slash(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    guild_ids = guildids
    bot = commands.Bot(command_prefix="/",
                       intents=discord.Intents.all())

    @commands.Cog.listener()
    async def on_ready(self):
        global startTime
        startTime = time.time()


    @cog_ext.cog_subcommand(
        base='utility',
        name='ping',
        description='Shows the ping and uptime of the bot',
        guild_ids=guild_ids
    )
    async def ping(self, ctx):
        embed=discord.Embed(title='Ping and Uptime', color=0x205675)
        embed.add_field(name='Ping', value=f"{round(self.bot.latency * 1000)}ms", inline=False)
        embed.add_field(name='Uptime', value=str(datetime.timedelta(seconds=int(round(time.time()-startTime)))), inline=False)
        await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base='fun',
        name='randomdog',
        description='Shows a random photo of a dog',
        guild_ids=guild_ids
    )
    
    async def doggo(self, ctx):
        async with aiohttp.ClientSession() as session:
            request = await session.get('https://some-random-api.ml/img/dog')
            dogjson = await request.json()
            request2 = await session.get('https://some-random-api.ml/facts/dog')
            dogfactjson = await request2.json()

            embed = discord.Embed(title='Woof!', color=0x205675)
            embed.set_image(url=dogjson['link'])
            embed.set_footer(text=dogfactjson['fact'])
            await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base='fun',
        name='randomcat',
        description='Generates a random picture of a cat.',
        guild_ids=guild_ids
    )
    async def cat(self, ctx):
        async with aiohttp.ClientSession() as session:
            request = await session.get('https://some-random-api.ml/img/cat')
            catjson = await request.json()
            request2 = await session.get('https://some-random-api.ml/facts/cat')
            catfactjson = await request2.json()

            embed = discord.Embed(title="Meow!", color=0x205675)
            embed.set_image(url=catjson['link'])
            embed.set_footer(text=catfactjson['fact'])
            await ctx.send(embed=embed)
    
    @cog_ext.cog_subcommand(
        base='fun',
        name='randomfact',
        description='Generate a random fact',
        guild_ids=guild_ids,
        options=[manage_commands.create_option(
            name='category',
            description='What kind of fact would you like?',
            option_type=3,
            choices=[manage_commands.create_choice(
                name='computer',
                value='computer'
            ),
            manage_commands.create_choice(
                name='food',
                value='food'
            ),
            manage_commands.create_choice(
                name='emoji',
                value='emoji'
            ),
            manage_commands.create_choice(
                name='space',
                value='space'
            ),
            manage_commands.create_choice(
                name='animal',
                value='animal'
            )],
        required=True)])

    async def fact(self, ctx, category: str):

        facts = factful.facts()
        if category == 'computer':
            embed=discord.Embed(title="Random Fact", description=facts["computer"], color=0x205675)
            embed.set_footer(text="Fact Topic: Computers")
            await ctx.send(embed=embed)
        if category == 'food':
            embed=discord.Embed(title="Random Fact", description=facts["food"], color=0x205675)
            embed.set_footer(text="Fact Topic: Food")
            await ctx.send(embed=embed)
        if category == 'emoji':
            embed=discord.Embed(title="Random Fact", description=facts["emoji"], color=0x205675)
            embed.set_footer(text="Fact Topic: Emoji")
            await ctx.send(embed=embed)
        if category == 'space':
            embed=discord.Embed(title="Random Fact", description=facts["space"], color=0x205675)
            embed.set_footer(text="Fact Topic: Space")
            await ctx.send(embed=embed)
        if category == 'animal':
            async with aiohttp.ClientSession() as session:
                request = await session.get('https://some-random-api.ml/facts/dog')
                factsjson = await request.json()
                
                # embed=discord.Embed(title="Random Fact", description=factsjson['fact'], color=0x205675)
                # embed.set_footer(text="Fact Topic: Dog")
                # await ctx.send(embed=embed)
                await ctx.send(factsjson['fact'])



    @cog_ext.cog_subcommand(
        base='fun',
        name='lyrics',
        description='Get the lyrics of a song',
        guild_ids=guild_ids,
        options=[manage_commands.create_option(
            name='song',
            description='Name of the song you want the lyrics of',
            option_type=3,
            required=True
        )]
    )
    
    async def lyric(self, ctx, *, song=None):

        song = song.replace(' ', '%20')

        async with aiohttp.ClientSession() as lyricsSession:
            async with lyricsSession.get(f'https://some-random-api.ml/lyrics?title={song}') as jsondata:
                if not ( 300 > jsondata.status >= 200 ):
                    await ctx.send(f'Song not found. Please try again.')
                    return
                else:
                    lyricsData = await jsondata.json()

            songLyrics = lyricsData['lyrics']
            songArtist = lyricsData['author']
            songTitle = lyricsData['title']

            try:
                for chunk in [songLyrics[i:i+2000] for i in range(  0  , len(songLyrics), 2000)]:
                    embed = discord.Embed(title=f'{songTitle} by {songArtist}', description=chunk, color=0x205675)
                    embed.set_footer(text="This message may have been split in half. This is due to Discord's 2000 character limit.")

                    await lyricsSession.close()

                    await ctx.send(embed=embed, hidden=True)

            except discord.HTTPException:
                embed = discord.Embed(title=f'{songTitle} by {songArtist}', description=chunk, color=0x205675)

                await lyricsSession.close()

                await ctx.send(embed=embed, hidden=True)

    @cog_ext.cog_subcommand(
        base='fun',
        name='filter',
        description='Put a special filter over a persons avatar.',
        guild_ids=guild_ids,
        options=[manage_commands.create_option(
            name='user',
            description='The person whos avatar you want to filter.',
            option_type=6,
            required=True
        ),
        manage_commands.create_option(
            name='filter',
            description='The filter you want to put on the persons avatar.',
            option_type=3,
            choices=[manage_commands.create_choice(
                name='wasted',
                value='wasted'
            ),
            manage_commands.create_choice(
                name='triggered',
                value='triggered'
            ),
            manage_commands.create_choice(
                name='glass',
                value='glass'
            ),
            manage_commands.create_choice(
                name='rainbow',
                value='rainbow'
            )],
        required=True)]
    )

    async def filter(self, ctx,user: discord.Member, filter: str):

        if filter == 'wasted':
            async with aiohttp.ClientSession() as wastedSession:
                async with wastedSession.get(f'https://some-random-api.ml/canvas/wasted?avatar={user.avatar_url_as(format="png", size=1024)}') as wastedImage:

                    imageData = io.BytesIO(await wastedImage.read())

                    await wastedSession.close()
                    await ctx.send(file=discord.File(imageData, 'wasted.png'))

        if filter == 'triggered':
            async with aiohttp.ClientSession() as triggeredSession:
                async with triggeredSession.get(f'https://some-random-api.ml/canvas/triggered?avatar={user.avatar_url_as(format="png", size=1024)}') as triggeredImage:

                    imageData = io.BytesIO(await triggeredImage.read())
                    
                    await triggeredSession.close()
                    await ctx.send(file=discord.File(imageData, 'triggered.gif'))

        if filter == 'glass':
            async with aiohttp.ClientSession() as glassSession:
                async with glassSession.get(f'https://some-random-api.ml/canvas/glass?avatar={user.avatar_url_as(format="png", size=1024)}') as glassImage:
                    
                    imageData = io.BytesIO(await glassImage.read())

                    await glassSession.close()
                    await ctx.send(file=discord.File(imageData, 'glass.png'))

        if filter == 'rainbow':
            async with aiohttp.ClientSession() as rainbowSession:
                async with rainbowSession.get(f'https://some-random-api.ml/canvas/gay?avatar={user.avatar_url_as(format="png", size=1024)}') as rainbowImage:
                    
                    imageData = io.BytesIO(await rainbowImage.read())

                    await rainbowSession.close()
                    await ctx.send(file=discord.File(imageData, 'rainbow.png'))
    @cog_ext.cog_subcommand(
        base='fun',
        name='ytcomment',
        description='Make a fake youtube comment.',
        guild_ids=guild_ids,
        options=[manage_commands.create_option(
            name='avatarlink',
            description='The link to the image on the comment',
            option_type=3,
            required=True
        ),
        manage_commands.create_option(
            name='username',
            description='The username of the user in the comment',
            option_type=3,
            required=True
        ),
        manage_commands.create_option(
            name='comment',
            description='What you want to comment to say',
            option_type=3,
            required=True
        )]
    )

    async def yt(self, ctx, avatarlink: str, username: str, comment: str):
        async with aiohttp.ClientSession() as youtubeSession:
                async with youtubeSession.get(f'https://some-random-api.ml/canvas/youtube-comment?avatar={avatarlink}&username={username}&comment={comment}') as youtubeImage:
                    
                    imageData = io.BytesIO(await youtubeImage.read())

                    await youtubeSession.close()
                    await ctx.send(file=discord.File(imageData, 'comment.png'))

    
    @cog_ext.cog_subcommand(
        base='fun',
        name='tweet',
        description='Create a fake tweet',
        guild_ids=guild_ids,
        options=[manage_commands.create_option(
            name='avatar',
            description='Link to an image for the avatar',
            option_type=3,
            required=True
        ),
        manage_commands.create_option(
            name='username',
            description='Username of the tweeter',
            option_type=3,
            required=True
        ),
        manage_commands.create_option(
            name='displayname',
            description='Display name of the tweeter',
            option_type=3,
            required=True
        ),
        manage_commands.create_option(
            name='message',
            description='Message in the tweet',
            option_type=3,
            required=True
        ),
        manage_commands.create_option(
            name='replies',
            description='Amount of replies on the tweet',
            option_type=4,
            required=True
        ),
        manage_commands.create_option(
            name='likes',
            description='Amount of likes on the tweet',
            option_type=4,
            required=True
        ),
        manage_commands.create_option(
            name='retweets',
            description='Amount of retweets on the tweet',
            option_type=4,
            required=True
        )]
    )

    async def tweet(self, ctx, avatar: str, username: str, displayname: str, message:str, replies: int, likes: int, retweets: int):
        async with aiohttp.ClientSession() as twitterSession:
            async with twitterSession.get(f'https://some-random-api.ml/canvas/tweet?avatar={avatar}&username={username}&displayname={displayname}&comment={message}&replies={replies}&likes={likes}&retweets={retweets}') as twitterImage:
                    
                imageData = io.BytesIO(await twitterImage.read())

                await twitterSession.close()
                await ctx.send(file=discord.File(imageData, 'tweet.png'))

    @cog_ext.cog_subcommand(
        base='fun',
        name='simpcard',
        description='Make someone a dedicated simpcard',
        guild_ids=guild_ids,
        options=[manage_commands.create_option(
            name='avatar',
            description='The avatar you want on the simp card',
            option_type=3,
            required=True
        )]
    )

    async def simp(self, ctx, avatar: str):
        async with aiohttp.ClientSession() as simpSession:
            async with simpSession.get(f'https://some-random-api.ml/canvas/simpcard?avatar={avatar}') as simpImage:
                    
                imageData = io.BytesIO(await simpImage.read())

                await simpSession.close()
                await ctx.send(file=discord.File(imageData, 'simpcard.png'))

    @cog_ext.cog_subcommand(
        base='fun',
        name='pokedex',
        description='Get the pokedex entry of a pokemon',
        guild_ids=guild_ids,
        options=[manage_commands.create_option(
            name='pokemon',
            description='The pokemon for the dex entry',
            option_type=3,
            required=True
        )]
    )
    async def pokedex(self, ctx, pokemon: str):

        async with aiohttp.ClientSession() as pokeSession:
                async with pokeSession.get(f'https://some-random-api.ml/pokedex?pokemon={pokemon}') as jsondata:
                    if not ( 300 > jsondata.status >= 200 ):
                        await ctx.send(f'Unable to find pokemon by the name of {pokemon}. If you were looking for Nidoran male or female, put a -m or -f after Nidoran.', hidden=True)
                        return
                    else:
                        pokeData = await jsondata.json()
                    
                    name = pokeData['name']
                    iD = pokeData['id']
                    typE = pokeData['type']
                    species = pokeData['species']
                    abilities = pokeData['abilities']
                    height = pokeData['height']
                    weight = pokeData['weight']
                    base_exp = pokeData['base_experience']
                    gender = pokeData['gender']
                    egg_groups = pokeData['egg_groups']
                    stats = pokeData['stats']
                    hp = stats['hp']
                    attack = stats['attack']
                    defense = stats['defense']
                    sp_atk = stats['sp_atk']
                    sp_def = stats['sp_def']
                    speed = stats['speed']
                    totalstats = stats['total']
                    family = pokeData['family']
                    evostage = family['evolutionStage']
                    evoline = family['evolutionLine']
                    sprites = pokeData['sprites']
                    normalSprite = sprites['normal']
                    animatedSprite = sprites['animated']
                    description = pokeData['description']
                    generation = pokeData['generation']

                    everything = name, iD, typE, species, abilities, height, weight, base_exp, gender, egg_groups, stats, hp, attack, defense, sp_atk, sp_def, speed, totalstats, family, evostage, evoline, sprites, animatedSprite, description, generation, normalSprite

                    try:
                        for chunk in [everything[i:i+2000] for i in range(  0  , len(everything), 2000)]:
                            if evoline == []:
                                pokemon_name = name[0].upper()+name[1:]
                                embed=discord.Embed(title=f"{pokemon_name}", description=f"{description}", color=0x205675)
                                embed.set_thumbnail(url = animatedSprite)
                                embed.set_author(name="Poke Info", icon_url = 'https://www.bizak.es/wp-content/uploads/2017/10/LOGO-POKEMON.png')
                                embed.add_field(name="ID", value=f"{iD}", inline=True)
                                embed.add_field(name="Species", value=', '.join(species), inline=True)
                                embed.add_field(name="Abilities", value=', '.join(abilities), inline=True)
                                embed.add_field(name="Height", value=f"{height}", inline=True)
                                embed.add_field(name="Weight", value=f"{weight}", inline=True)
                                embed.add_field(name="Base Exp", value=f"{base_exp}", inline=True)
                                embed.add_field(name="Gender Percentage", value=f', '.join(gender), inline=True)
                                embed.add_field(name="Egg Groups", value=', '.join(egg_groups), inline=True)
                                embed.add_field(name="Type", value=', '.join(typE), inline=True)
                                embed.add_field(name="HP Stat", value=f"{hp}", inline=True)
                                embed.add_field(name="Attack Stat", value=f"{attack}", inline=True)
                                embed.add_field(name="Defense Stat", value=f"{defense}", inline=True)
                                embed.add_field(name="Special Attack Stat", value=f"{sp_atk}", inline=True)
                                embed.add_field(name="Special Defense Stat", value=f"{sp_def}", inline=True)
                                embed.add_field(name="Speed Stat", value=f"{speed}", inline=True)
                                embed.add_field(name="Stat Total", value=f"{totalstats}", inline=True)
                                embed.add_field(name="Evolution Stage", value=f"{evostage}", inline=True)
                                embed.add_field(name="Evolution Line", value=f"None", inline=True)
                                embed.add_field(name="When Added", value=f"Gen {generation}", inline=False)
                                embed.set_image(url = normalSprite)

                                await pokeSession.close()
                                await ctx.send(embed=embed, hidden=True)
                            
                            else:
                                pokemon_name = name[0].upper()+name[1:]
                                embed=discord.Embed(title=f"{pokemon_name}", description=f"{description}", color=0x205675)
                                embed.set_thumbnail(url = animatedSprite)
                                embed.set_author(name="Poke Info", icon_url = 'https://www.bizak.es/wp-content/uploads/2017/10/LOGO-POKEMON.png')
                                embed.add_field(name="ID", value=f"{iD}", inline=True)
                                embed.add_field(name="Species", value=', '.join(species), inline=True)
                                embed.add_field(name="Abilities", value=', '.join(abilities), inline=True)
                                embed.add_field(name="Height", value=f"{height}", inline=True)
                                embed.add_field(name="Weight", value=f"{weight}", inline=True)
                                embed.add_field(name="Base Exp", value=f"{base_exp}", inline=True)
                                embed.add_field(name="Gender Percentage", value=', '.join(gender), inline=True)
                                embed.add_field(name="Egg Groups", value=', '.join(egg_groups), inline=True)
                                embed.add_field(name="Type", value=', '.join(typE), inline=True)
                                embed.add_field(name="HP Stat", value=f"{hp}", inline=True)
                                embed.add_field(name="Attack Stat", value=f"{attack}", inline=True)
                                embed.add_field(name="Defense Stat", value=f"{defense}", inline=True)
                                embed.add_field(name="Special Attack Stat", value=f"{sp_atk}", inline=True)
                                embed.add_field(name="Special Defense Stat", value=f"{sp_def}", inline=True)
                                embed.add_field(name="Speed Stat", value=f"{speed}", inline=True)
                                embed.add_field(name="Stat Total", value=f"{totalstats}", inline=True)
                                embed.add_field(name="Evolution Stage", value=f"{evostage}", inline=True)
                                embed.add_field(name="Evolution Line", value=', '.join(evoline), inline=True)
                                embed.add_field(name="When Added", value=f"Gen {generation}", inline=False)
                                embed.set_image(url = normalSprite)

                                await pokeSession.close()
                                await ctx.send(embed=embed, hidden=True)

                            
                    except discord.HTTPException:
                        if evoline == []:
                            pokemon_name = name[0].upper()+name[1:]
                            embed=discord.Embed(title=f"{pokemon_name}", description=f"{description}", color=0x205675)
                            embed.set_thumbnail(url = animatedSprite)
                            embed.set_author(name="Poke Info", icon_url = 'https://www.bizak.es/wp-content/uploads/2017/10/LOGO-POKEMON.png')
                            embed.add_field(name="ID", value=f"{iD}", inline=True)
                            embed.add_field(name="Species", value=', '.join(species), inline=True)
                            embed.add_field(name="Abilities", value=', '.join(abilities), inline=True)
                            embed.add_field(name="Height", value=f"{height}", inline=True)
                            embed.add_field(name="Weight", value=f"{weight}", inline=True)
                            embed.add_field(name="Base Exp", value=f"{base_exp}", inline=True)
                            embed.add_field(name="Gender Percentage", value=', '.join(gender), inline=True)
                            embed.add_field(name="Egg Groups", value=', '.join(egg_groups), inline=True)
                            embed.add_field(name="Type", value=', '.join(typE), inline=True)
                            embed.add_field(name="HP Stat", value=f"{hp}", inline=True)
                            embed.add_field(name="Attack Stat", value=f"{attack}", inline=True)
                            embed.add_field(name="Defense Stat", value=f"{defense}", inline=True)
                            embed.add_field(name="Special Attack Stat", value=f"{sp_atk}", inline=True)
                            embed.add_field(name="Special Defense Stat", value=f"{sp_def}", inline=True)
                            embed.add_field(name="Speed Stat", value=f"{speed}", inline=True)
                            embed.add_field(name="Stat Total", value=f"{totalstats}", inline=True)
                            embed.add_field(name="Evolution Stage", value=f"{evostage}", inline=True)
                            embed.add_field(name="Evolution Line", value="None", inline=True)
                            embed.add_field(name="When Added", value=f"Gen {generation}", inline=False)
                            embed.set_image(url = normalSprite)

                            await pokeSession.close()
                            await ctx.send(embed=embed, hidden=True)
                        else:
                            pokemon_name = name[0].upper()+name[1:]
                            embed=discord.Embed(title=f"{pokemon_name}", description=f"{description}", color=0x205675)
                            embed.set_thumbnail(url = animatedSprite)
                            embed.set_author(name="Poke Info", icon_url = 'https://www.bizak.es/wp-content/uploads/2017/10/LOGO-POKEMON.png')
                            embed.add_field(name="ID", value=f"{iD}", inline=True)
                            embed.add_field(name="Species", value=', '.join(species), inline=True)
                            embed.add_field(name="Abilities", value=', '.join(abilities), inline=True)
                            embed.add_field(name="Height", value=f"{height}", inline=True)
                            embed.add_field(name="Weight", value=f"{weight}", inline=True)
                            embed.add_field(name="Base Exp", value=f"{base_exp}", inline=True)
                            embed.add_field(name="Gender Percentage", value=', '.join(gender), inline=True)
                            embed.add_field(name="Egg Groups", value=', '.join(egg_groups), inline=True)
                            embed.add_field(name="Type", value=', '.join(typE), inline=True)
                            embed.add_field(name="HP Stat", value=f"{hp}", inline=True)
                            embed.add_field(name="Attack Stat", value=f"{attack}", inline=True)
                            embed.add_field(name="Defense Stat", value=f"{defense}", inline=True)
                            embed.add_field(name="Special Attack Stat", value=f"{sp_atk}", inline=True)
                            embed.add_field(name="Special Defense Stat", value=f"{sp_def}", inline=True)
                            embed.add_field(name="Speed Stat", value=f"{speed}", inline=True)
                            embed.add_field(name="Stat Total", value=f"{totalstats}", inline=True)
                            embed.add_field(name="Evolution Stage", value=f"{evostage}", inline=True)
                            embed.add_field(name="Evolution Line", value=', '.join(evoline), inline=True)
                            embed.add_field(name="When Added", value=f"Gen {generation}", inline=False)
                            embed.set_image(url = normalSprite)

                            await pokeSession.close()
                            await ctx.send(embed=embed, hidden=True)
                    
    @has_permissions(administrator=True)
    @cog_ext.cog_subcommand(
        base='welcome',
        name='welcomesettings',
        description='Set the settings for the welcome message',
        guild_ids=guild_ids,
        options=[manage_commands.create_option(
            name='template',
            description='A number 1-4 for the welcome template',
            option_type=4,
            required=True
            
        ),
        manage_commands.create_option(
            name='channel',
            description='The channel where you want welcome messages sent',
            option_type=7,
            required=True
        ),
        manage_commands.create_option(
            name='background',
            description='A background for your welcome message',
            option_type=3,
            choices = [manage_commands.create_choice(
                name='stars',
                value='stars'
            ),
            manage_commands.create_choice(
                name='stars2',
                value='stars2'
            ),
            manage_commands.create_choice(
                name='rainbowgradient',
                value='rainbowgradient'
            ),
            manage_commands.create_choice(
                name='rainbow',
                value='rainbow'
            ),
            manage_commands.create_choice(
                name='sunset',
                value='sunset'
            ),
            manage_commands.create_choice(
                name='night',
                value='night'
            ),
            manage_commands.create_choice(
                name='blobday',
                value='blobday'
            ),
            manage_commands.create_choice(
                name='blobnight',
                value='blobnight'
            ),
            manage_commands.create_choice(
                name='space',
                value='space'
            ),
            manage_commands.create_choice(
                name='gaming1',
                value='gaming1'
            ),
            manage_commands.create_choice(
                name='gaming2',
                value='gaming2'
            ),
            manage_commands.create_choice(
                name='gaming3',
                value='gaming3'
            ),
            manage_commands.create_choice(
                name='gaming4',
                value='gaming4'
            )],
            required=True

        ),  
        manage_commands.create_option(
            name='textcolor',
            description='A text color for the welcome message',
            option_type=3,
            choices=[manage_commands.create_choice(
                name='red',
                value='red'
            ),
            manage_commands.create_choice(
                name='orange',
                value='orange'
            ),
            manage_commands.create_choice(
                name='yellow',
                value='yellow'
            ),
            manage_commands.create_choice(
                name='green',
                value='green'
            ),
            manage_commands.create_choice(
                name='blue',
                value='blue'
            ),
            manage_commands.create_choice(
                name='indigo',
                value='indigo'
            ),
            manage_commands.create_choice(
                name='purple',
                value='purple'
            ),
            manage_commands.create_choice(
                name='pink',
                value='pink'
            ),
            manage_commands.create_choice(
                name='black',
                value='black'
            ),
            manage_commands.create_choice(
                name='white',
                value='white'
            )],
            required=True
            
        )])
    
    async def welcomeconfig(self, ctx, template: int, background: str, textcolor: str, channel: discord.TextChannel):
        
        if template > 4:
            await ctx.send("You must put a number between 1 and 4.")
            return
        else: 
            # post = {'guild_id': f'{ctx.guild.id}'},
            # {"$set": {'welcome': True, 'welcomeChannel': f'{channel}', 'welcomeTemplate': f'{template}', 'welcomeBackground': f'{background}', 'welcomeTextcolor': f'{textcolor}'}}
            collection.update_one({'guild_id': f'{ctx.guild.id}'},
            {"$set": {'welcome': True, 'welcomeChannel': f'{channel.id}', 'welcomeTemplate': f'{template}', 'welcomeBackground': f'{background}', 'welcomeTextcolor': f'{textcolor}'}})
            await ctx.send("Welcome messages are set up. To check what your welcome message will look like, do /welcome preview and insert the same parameters you inserted in this command except for the channel.")


    @has_permissions(administrator=True)
    @cog_ext.cog_subcommand(
        base='goodbye',
        name='goodbyesettings',
        description='Set the settings for the goodbye message',
        guild_ids=guild_ids,
        options=[manage_commands.create_option(
            name='template',
            description='A number 1-4 for the goodbye template',
            option_type=4,
            required=True
            
        ),
        manage_commands.create_option(
            name='channel',
            description='The channel where you want goodbye messages sent',
            option_type=7,
            required=True
        ),
        manage_commands.create_option(
            name='background',
            description='A background for your goodbye message',
            option_type=3,
            choices = [manage_commands.create_choice(
                name='stars',
                value='stars'
            ),
            manage_commands.create_choice(
                name='stars2',
                value='stars2'
            ),
            manage_commands.create_choice(
                name='rainbowgradient',
                value='rainbowgradient'
            ),
            manage_commands.create_choice(
                name='rainbow',
                value='rainbow'
            ),
            manage_commands.create_choice(
                name='sunset',
                value='sunset'
            ),
            manage_commands.create_choice(
                name='night',
                value='night'
            ),
            manage_commands.create_choice(
                name='blobday',
                value='blobday'
            ),
            manage_commands.create_choice(
                name='blobnight',
                value='blobnight'
            ),
            manage_commands.create_choice(
                name='space',
                value='space'
            ),
            manage_commands.create_choice(
                name='gaming1',
                value='gaming1'
            ),
            manage_commands.create_choice(
                name='gaming2',
                value='gaming2'
            ),
            manage_commands.create_choice(
                name='gaming3',
                value='gaming3'
            ),
            manage_commands.create_choice(
                name='gaming4',
                value='gaming4'
            )],
            required=True

        ),  
        manage_commands.create_option(
            name='textcolor',
            description='A text color for the goodbye message',
            option_type=3,
            choices=[manage_commands.create_choice(
                name='red',
                value='red'
            ),
            manage_commands.create_choice(
                name='orange',
                value='orange'
            ),
            manage_commands.create_choice(
                name='yellow',
                value='yellow'
            ),
            manage_commands.create_choice(
                name='green',
                value='green'
            ),
            manage_commands.create_choice(
                name='blue',
                value='blue'
            ),
            manage_commands.create_choice(
                name='indigo',
                value='indigo'
            ),
            manage_commands.create_choice(
                name='purple',
                value='purple'
            ),
            manage_commands.create_choice(
                name='pink',
                value='pink'
            ),
            manage_commands.create_choice(
                name='black',
                value='black'
            ),
            manage_commands.create_choice(
                name='white',
                value='white'
            )],
            required=True
            
        )])
    
    async def goodbyeconfig(self, ctx, template: int, background: str, textcolor: str, channel: discord.TextChannel):
        
        if template > 4:
            await ctx.send("You must put a number between 1 and 4.")
            return
        else: 
            # post = {'guild_id': f'{ctx.guild.id}'},
            # {"$set": {'welcome': True, 'welcomeChannel': f'{channel}', 'welcomeTemplate': f'{template}', 'welcomeBackground': f'{background}', 'welcomeTextcolor': f'{textcolor}'}}
            collection.update_one({'guild_id': f'{ctx.guild.id}'},
            {"$set": {'goodbye': True, 'goodbyeChannel': f'{channel.id}', 'goodbyeTemplate': f'{template}', 'goodbyeBackground': f'{background}', 'goodbyeTextColor': f'{textcolor}'}})
            await ctx.send("Goodbye messages are set up. To preview what your goodbye message will look like, do /goodbye preview and insert the same parameters you inserted in this command except for the channel.")

    @has_permissions(administrator=True)
    @cog_ext.cog_subcommand(
        base='goodbye',
        name='preview',
        description='Preview what your goodbye message will look like',
        guild_ids=guild_ids,
        options=[manage_commands.create_option(
            name='template',
            description='A number 1-4 for the goodbye template',
            option_type=4,
            required=True
            
        ),
        manage_commands.create_option(
            name='background',
            description='A background for your goodbye message',
            option_type=3,
            choices = [manage_commands.create_choice(
                name='stars',
                value='stars'
            ),
            manage_commands.create_choice(
                name='stars2',
                value='stars2'
            ),
            manage_commands.create_choice(
                name='rainbowgradient',
                value='rainbowgradient'
            ),
            manage_commands.create_choice(
                name='rainbow',
                value='rainbow'
            ),
            manage_commands.create_choice(
                name='sunset',
                value='sunset'
            ),
            manage_commands.create_choice(
                name='night',
                value='night'
            ),
            manage_commands.create_choice(
                name='blobday',
                value='blobday'
            ),
            manage_commands.create_choice(
                name='blobnight',
                value='blobnight'
            ),
            manage_commands.create_choice(
                name='space',
                value='space'
            ),
            manage_commands.create_choice(
                name='gaming1',
                value='gaming1'
            ),
            manage_commands.create_choice(
                name='gaming2',
                value='gaming2'
            ),
            manage_commands.create_choice(
                name='gaming3',
                value='gaming3'
            ),
            manage_commands.create_choice(
                name='gaming4',
                value='gaming4'
            )],
            required=True

        ),  
        manage_commands.create_option(
            name='textcolor',
            description='A text color for the goodbye message',
            option_type=3,
            choices=[manage_commands.create_choice(
                name='red',
                value='red'
            ),
            manage_commands.create_choice(
                name='orange',
                value='orange'
            ),
            manage_commands.create_choice(
                name='yellow',
                value='yellow'
            ),
            manage_commands.create_choice(
                name='green',
                value='green'
            ),
            manage_commands.create_choice(
                name='blue',
                value='blue'
            ),
            manage_commands.create_choice(
                name='indigo',
                value='indigo'
            ),
            manage_commands.create_choice(
                name='purple',
                value='purple'
            ),
            manage_commands.create_choice(
                name='pink',
                value='pink'
            ),
            manage_commands.create_choice(
                name='black',
                value='black'
            ),
            manage_commands.create_choice(
                name='white',
                value='white'
            )],
            required=True
            
        )])
    async def gpreview(self, ctx, template: int, background: str, textcolor: str):

        if template > 4:
            await ctx.send("The template number must be between 1 and 4")
        else:
            member = ctx.author
            username = member.name
            discriminator = member.discriminator
            guildname = member.guild.name
            guildmembercount = len(member.guild.members)

            async with aiohttp.ClientSession() as goodbyeSession:
                async with goodbyeSession.get(f'https://some-random-api.ml/welcome/img/{template}/{background}?type=join&username={username}&discriminator={discriminator}&avatar={member.avatar_url_as(format="png", size=1024)}&guildName={guildname}&memberCount={guildmembercount}&textcolor={textcolor}') as image_resp:
                    goodbyeImage = io.BytesIO(await image_resp.read())

                    await goodbyeSession.close()
                    await ctx.send(file=discord.File(goodbyeImage, 'goodbye.png'))

    @has_permissions(administrator=True)
    @cog_ext.cog_subcommand(
        base='welcome',
        name='preview',
        description='Preview what your welcome message will look like',
        guild_ids=guild_ids,
        options=[manage_commands.create_option(
            name='template',
            description='A number 1-4 for the welcome template',
            option_type=4,
            required=True
            
        ),
        manage_commands.create_option(
            name='background',
            description='A background for your welcome message',
            option_type=3,
            choices = [manage_commands.create_choice(
                name='stars',
                value='stars'
            ),
            manage_commands.create_choice(
                name='stars2',
                value='stars2'
            ),
            manage_commands.create_choice(
                name='rainbowgradient',
                value='rainbowgradient'
            ),
            manage_commands.create_choice(
                name='rainbow',
                value='rainbow'
            ),
            manage_commands.create_choice(
                name='sunset',
                value='sunset'
            ),
            manage_commands.create_choice(
                name='night',
                value='night'
            ),
            manage_commands.create_choice(
                name='blobday',
                value='blobday'
            ),
            manage_commands.create_choice(
                name='blobnight',
                value='blobnight'
            ),
            manage_commands.create_choice(
                name='space',
                value='space'
            ),
            manage_commands.create_choice(
                name='gaming1',
                value='gaming1'
            ),
            manage_commands.create_choice(
                name='gaming2',
                value='gaming2'
            ),
            manage_commands.create_choice(
                name='gaming3',
                value='gaming3'
            ),
            manage_commands.create_choice(
                name='gaming4',
                value='gaming4'
            )],
            required=True

        ),  
        manage_commands.create_option(
            name='textcolor',
            description='A text color for the welcome message',
            option_type=3,
            choices=[manage_commands.create_choice(
                name='red',
                value='red'
            ),
            manage_commands.create_choice(
                name='orange',
                value='orange'
            ),
            manage_commands.create_choice(
                name='yellow',
                value='yellow'
            ),
            manage_commands.create_choice(
                name='green',
                value='green'
            ),
            manage_commands.create_choice(
                name='blue',
                value='blue'
            ),
            manage_commands.create_choice(
                name='indigo',
                value='indigo'
            ),
            manage_commands.create_choice(
                name='purple',
                value='purple'
            ),
            manage_commands.create_choice(
                name='pink',
                value='pink'
            ),
            manage_commands.create_choice(
                name='black',
                value='black'
            ),
            manage_commands.create_choice(
                name='white',
                value='white'
            )],
            required=True
            
        )])
    async def preview(self, ctx, template: int, background: str, textcolor: str):

        if template > 4:
            await ctx.send("The template number must be between 1 and 4")
        else:
            member = ctx.author
            username = member.name
            discriminator = member.discriminator
            guildname = member.guild.name
            guildmembercount = len(member.guild.members)

            async with aiohttp.ClientSession() as welcomeSession:
                async with welcomeSession.get(f'https://some-random-api.ml/welcome/img/{template}/{background}?type=join&username={username}&discriminator={discriminator}&avatar={member.avatar_url_as(format="png", size=1024)}&guildName={guildname}&memberCount={guildmembercount}&textcolor={textcolor}') as image_resp:
                    welcomeImage = io.BytesIO(await image_resp.read())

                    await welcomeSession.close()
                    await ctx.send(file=discord.File(welcomeImage, 'welcome.png'))

    @has_permissions(administrator=True)
    @cog_ext.cog_subcommand(
        base='config',
        name='botcommandschannel',
        description='Set a bot commands channel',
        guild_ids=guild_ids,
        options=[manage_commands.create_option(
            name='channel',
            description='The channel where you want the bot commands to be sent',
            option_type=7,
            required=True
        )])

    async def botcommands(self, ctx, channel: discord.TextChannel):

        collection.update_one({'guild_id': f'{ctx.guild.id}'}, {"$set":{"botCommandsChannel": f'{channel.id}'}})

        await ctx.send(f"Bot commands channel set to {channel}")

    

    # @has_permissions(administrator=True)
    # @cog_ext.cog_subcommand(
    #     base='fun',
    #     name='gstart',
    #     description='Start a giveaway',
    #     guild_ids=guild_ids,
    #     options=[manage_commands.create_option(
    #         name='channel',
    #         description='The channel where the giveaway will be sent',
    #         option_type=3,
    #         required=True
    #     ),
    #     manage_commands.create_option(
    #         name='time',
    #         description='Amount of time the giveaway will run for. Examples: 3s, 5m, 7h, or 9d',
    #         option_type=3,
    #         required=True
    #     ),
    #     manage_commands.create_option(
    #         name='prize',
    #         description='The prize for the giveaway',
    #         option_type=3,
    #         required=True
    #     )]
    # )

    # async def start(self, ctx, channel: str, time: str, *,  prize: str,):
    #     bot = commands.Bot(command_prefix="/",
    #                    intents=discord.Intents.all())

    #     channel = {channel}

    #     time_conversion = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    #     giveawaytime = int(time[0]) * time_conversion[time[-1]]

    #     embed = discord.Embed(title='New Giveaway!', description=f"{prize}", color=0x205675)
    #     embed.add_field(name="Duration", value=giveawaytime)
    #     embed.set_footer(text=f"Hosted by: {ctx.author.mention}")

    #     msg = await ctx.send(embed=embed)
    #     await msg.add_reaction("🎉")

    #     await asyncio.sleep(giveawaytime)

    #     msg2 = await ctx.channel.fetch_message(msg.id)
    #     users = await msg2.reactions[0].users().flatten()
    #     users.pop(users.index(bot.user))

    #     winner = random.choice(users)
    #     await channel.send(f"Congrats! {winner.mention} won {prize}!!")


    @cog_ext.cog_subcommand(
    base='fun',
    name='Amongus',
    description='Put someones avatar on an amongus character',
    guild_ids=guild_ids,
    options=[manage_commands.create_option(
        name='user',
        description='The user you want to make an amongus character',
        option_type=6,
        required=True
    )])
    # manage_commands.create_option(
    #     name='impostor',
    #     description='Do you want the character to be an impostor?',
    #     option_type=5,
    #     required=True
    # )]
    
    async def amogus(self, ctx, user: discord.Member):

        apikey = '3hTp422CPc4WMAgNeFlgSKjPC'
    
        try: 

            async with aiohttp.ClientSession() as amongusSession:
                async with amongusSession.get(f'https://some-random-api.ml/premium/amongus?username={user.name}&avatar={user.avatar_url_as(format="png")}&key={apikey}') as amongusImage:

                    imageData = io.BytesIO(await amongusImage.read())
                    
                    await amongusSession.close()
                    await ctx.send(file=discord.File(imageData, 'amogus.gif'))
        except discord.HTTPException:
            async with aiohttp.ClientSession() as amongusSession:
                async with amongusSession.get(f'https://some-random-api.ml/premium/amongus?username={user.name}&avatar={user.avatar_url_as(format="png")}&key={apikey}') as amongusImage:

                    imageData = io.BytesIO(await amongusImage.read())
                    
                    await amongusSession.close()
                    await ctx.send(file=discord.File(imageData, 'amogus.gif'))

    
                
            
                    
        

def setup(bot: commands.Bot):
    bot.add_cog(slash(bot))