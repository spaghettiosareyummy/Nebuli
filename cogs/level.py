import discord
from discord_slash import SlashCommand
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils import manage_commands
from discord_slash.model import SlashCommandOptionType
from credsfile import NEBULI, guildids, MONGOLINK, CLUSTER, COLLECTION, COLLECTIONLEVEL
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
collectionlevel = db[COLLECTIONLEVEL]
# collection2 = db[COLLECTION]

class level(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    guild_ids = guildids
    bot = commands.Bot(command_prefix="/",
                       intents=discord.Intents.all())

    @commands.Cog.listener()
    async def on_message(self, message):

        if isinstance(message.channel, discord.channel.DMChannel):
            return

        stats = collectionlevel.find_one({"id": message.author.id})
        if not message.author.bot:
            
            if stats is None:
                newuser = {"guild_id": message.guild.id, "id" : message.author.id, "xp" : 0, "lvl" : 1}
                collectionlevel.insert_one(newuser)
            else:
                xp = stats["xp"]
                finalxp = xp + 5
                
                collectionlevel.update_one({"guild_id":message.guild.id, "id": message.author.id}, {"$set": {"xp": finalxp}})
                
                lvl = 1
                while True:
                    if xp < ((50*(lvl**2))+(50*(lvl-1))):
                        break
                    lvl += 1
                xp -= ((50*((lvl-1)**2))+(50*(lvl-1)))
                if xp == 0:
                    await message.channel.send(f"Great job {message.author.mention}! You've leveled up to **level {lvl}**.")
                    collectionlevel.update_one({"guild_id": message.guild.id, "id": message.author.id}, {"$set": {"lvl": lvl}})
                
    @cog_ext.cog_subcommand(
        base='level',
        name='rank',
        description='Check your leveling rank',
        guild_ids=guild_ids
    )

    async def rank(self, ctx):
        # thing = collectionlevel.find_one({"guild_id": f'{ctx.guild.id}'})
        # channel = thing['botCommandsChannel']
        # channelid = int(channel)
        # botcommandschannel = await bot.fetch_channel(channel1)
        
        
        stats = collectionlevel.find_one({"id" : ctx.author.id})
        if stats is None:
            embed=discord.Embed(title="Rank: 0")
            embed.set_author(name=f"{ctx.author.name}'s rank", icon_url = ctx.author.avatar_url)
            embed.set_thumbnail(url = ctx.author.avatar_url)
            await ctx.send(embed=embed)
            
        else: 
            username = ctx.author.name
            avatar = ctx.author.avatar_url
            discriminator = ctx.author.discriminator
            key = "3hTp422CPc4WMAgNeFlgSKjPC"

            xp = stats["xp"]
            lvl = stats['lvl']
            rank = 0
            print("yes")
            while True:
                if xp < ((50*(lvl**2))+(50*(lvl-1))):
                    break
                lvl += 1
            xp -= ((50*((lvl-1)**2))+(50*(lvl-1)))
            boxes = int((xp/(200*((1/2) * lvl)))*20)
            rankings = collectionlevel.find().sort("xp",-1)
            neededxp = int(200*((1/2)*lvl))
            print("yes")

            for x in rankings:
                print("no")
                rank += 1
                print("maybe")
                # if stats["id"] == x["id"]:
                #     print("you")
                #     break
                print("me")
                    
            async with aiohttp.ClientSession() as rankcardSession:
                print("yes")
                async with rankcardSession.get(f'https://some-random-api.ml/premium/rankcard/1/?username=spaghetti&avatar=https://cdn.discordapp.com/avatars/323216758313844736/b18d7d92c40d9e44eddb4f3cd89bd269.png?size=256&discriminator=3019&level=3&cxp=130&nxp=300&rank=1&key=3hTp422CPc4WMAgNeFlgSKjPC') as image_resp:
                    rankcardImage = io.BytesIO(await image_resp.read())
                    print("yes")

                    await rankcardSession.close()
                    await ctx.send(file=discord.File(rankcardImage, 'rankcard.png'))


            
            # embed = discord.Embed(title=f"{ctx.author.name}'s level")
            # embed.add_field(name="XP", value=f"{xp}/{outof}", inline=True)
            # embed.add_field(name="Level", value=f'{lvl}', inline=True)
            # embed.add_field(name="Rank", value=f"{rank}/{ctx.guild.member_count}", inline=True)
            # embed.add_field(name="Progress Bar", value=boxes * ":blue_square:" + (20-boxes) * ":white_large_square:", inline=True)
            # embed.set_thumbnail(url=ctx.author.avatar_url)
            # await ctx.send(embed=embed)
            # if ctx.channel.id == channelid:
            #     await ctx.send(embed=embed)
            # elif ctx.channel.id != channelid:
            #     await ctx.send(embed=embed, hidden=True)
                

def setup(bot: commands.Bot):
    bot.add_cog(level(bot))