import discord
from discord_slash import SlashCommand
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils import manage_commands
from discord_slash.model import SlashCommandOptionType
from credsfile import NEBULI, guildids
from discord.ext.commands.core import has_permissions
from credsfile import NEBULI, MONGOLINK, CLUSTER, COLLECTION, COLLECTIONECO
import datetime, time
import asyncio
import aiohttp
import factful
import io
import random
import json
import os
import pymongo
from pymongo import MongoClient

cluster = MongoClient(MONGOLINK)
db = cluster[CLUSTER]
collection = db[COLLECTIONECO]



# def get_bank_data(user):
#         doc = collection.find_one({'user_id': f'{user.id}'})

def update_bank(user,change=0,mode="wallet"):
    doc = collection.find_one({'user_id': f'{user.id}'})

    
    newbal = doc[f'{mode}'] + change 

    updatedoc = collection.update_one({'user_id': f'{user.id}'}, {"$set": {{mode}: newbal}})

    

    balance = doc[f'wallet'], doc[f'bank']

    return balance
def open_account(user):

        doc = collection.find_one({'user_id': f'{user.id}'})
        if doc == None:
            post = {'user_id': f'{user.id}', 'wallet': 0, 'bank': 0}
            collection.insert_one(post)
            # sets data to their correct vars

        

        
       
        elif doc != None:
            return False
            #if user already has account, dont do anything

       

class eco(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    guild_ids = guildids
    



    @cog_ext.cog_subcommand(
        base='eco',
        name='balance',
        description='Check your account balance',
        guild_ids=guild_ids,
        options=[manage_commands.create_option(
            name='user',
            description="The user whos bank account you would like information on.",
            option_type=6,
            required=True
        )]
    )
    async def balance(self, ctx, user: discord.Member):
        
        open_account(ctx.author) #opening an account for the author
        

        # users = get_bank_data()
        doc = collection.find_one({'user_id': f'{user.id}'})
        if doc == None:
            await ctx.send("This user does not have an account.")
        if doc != None: 
            wallet_amount = doc['wallet']
            bank_amount = doc['bank']


            embed = discord.Embed(title=f"{user.name}'s balance", color=0x205675)
            embed.add_field(name="Wallet Amount", value=wallet_amount)
            embed.add_field(name="Bank Amount", value=bank_amount)
            await ctx.send(embed=embed)
        
    
    @cog_ext.cog_subcommand(
    base='eco',
    name='beg',
    description='Beg for money',
    guild_ids=guild_ids
    )
    async def beg(self, ctx):
        open_account(ctx.author)
        user = ctx.author
        doc = collection.find_one({'user_id': f'{user.id}'})
        # users = open_account(ctx.author)
        

        earnings = random.randrange(101)

        await ctx.send(f"You have been given {earnings} money!")

        newbal = doc["wallet"] + earnings
        updatedoc = collection.update_one({'user_id': f'{user.id}'}, {"$set": {'wallet': newbal}})


        update_bank(ctx.author, earnings)

    # @cog_ext.cog_subcommand(
    #     base='eco',
    #     name='withdraw',
    #     description='Withdraw money from your bank',
    #     guild_ids=guild_ids,
    #     options=[manage_commands.create_option(
    #             name='amount',
    #             description='Amount to withdraw',
    #             option_type=4,
    #             required=True
    #         )])
    # async def withdraw(self, ctx, amount: int):
    #     open_account(ctx.author)
    #     doc = collection.find_one({'user_id': f'{user.id}'})

    #     balance = update_bank(ctx.author)

    #     if amount > balance[1]:
    #         await ctx.send("You can't withdraw money that you don't have.")
    #         return
    #     if amount < 0:
    #         await ctx.send("The amount must be positive")

    #     update_bank(ctx.author, amount)
    #     update_bank(ctx.author, -1 * amount, "bank")
    #     await ctx.send(f"Successfully withdrew {amount} coins.")

    @cog_ext.cog_subcommand(
        base='eco',
        name='deposit',
        description='Depost money from your wallet to your bank',
        guild_ids=guild_ids,
        options=[manage_commands.create_option(
                name='amount',
                description='Amount to deposit',
                option_type=4,
                required=True
            )])
    async def deposit(self, ctx, amount: int):
        open_account(ctx.author)

        balance = update_bank(ctx.author)

        if amount > balance[0]:
            await ctx.send("You can't deposit money that you don't have.")
            return
        if amount < 0:
            await ctx.send("The amount must be positive")

        update_bank(ctx.author, -1 * amount)
        update_bank(ctx.author, amount, "bank")
        await ctx.send(f"Successfully deposited {amount} coins.")

    @cog_ext.cog_subcommand(
        base='eco',
        name='donate',
        description='Donate some money to someone in the server.',
        guild_ids=guild_ids,
        options=[manage_commands.create_option(
                name='amount',
                description='Amount to donate',
                option_type=4,
                required=True
            ),
            manage_commands.create_option(
                name='user',
                description='The user you are donating to.',
                option_type=6,
                required=True
            )])
    async def donate(self, ctx, amount: int, user: discord.Member):
        open_account(ctx.author)
        
        authoraccount = collection.find_one({'user_id': f'{ctx.author.id}'})
        authorwallet = authoraccount['wallet']

        doc = collection.find_one({'user_id': f'{user.id}'})
        
        if doc == None:
            await ctx.send("This user does not have an account set up.")
        elif doc != None:
            givenwallet = doc['wallet']

        open_account(ctx.author)
        


        if amount > authorwallet:
            await ctx.send("You can't donate money that you don't have.")
            return
        if amount < 0:
            await ctx.send("The amount must be positive")

        bal_for_giver = authorwallet - amount
        collection.update_one({'user_id': f'{ctx.author.id}'}, {"$set": {'wallet': bal_for_giver}})

        bal_for_given = givenwallet + amount
        collection.update_one({'user_id': f'{user.id}'}, {"$set": {'wallet': bal_for_given}})
        await ctx.send(f"Successfully donated {amount} coins to {user.name}.")

    @cog_ext.cog_subcommand(
        base='eco',
        name='slots',
        description='Take a trip to the casino and hopefully win some money.',
        guild_ids=guild_ids,
        options=[manage_commands.create_option(
            name='amount',
            description='The amount you are betting on slots',
            option_type=4,
            required=True
        )]
    )

    async def slots(self, ctx, amount: int):

        doc = collection.find_one({'user_id': f'{ctx.author.id}'})

        open_account(ctx.author)

        balance = doc['wallet']

        if amount > balance:
            await ctx.send("You can't bet money that you don't have.")
            return
        if amount < 0:
            await ctx.send("The amount must be positive")

        final = []

        for i in range(3):
            a = random.choice(["🎉", "⌚", "🧹"])

            final.append(a)

        await ctx.send(str(final))

        if final[0] == final[1] == final[2]:
            winbal = balance + amount
            collection.update_one({'user_id': f'{ctx.author.id}'}, {"$set": {'wallet': winbal}})
            await ctx.send("You won! The amount you bet has been added to your wallet")
        else:

            loosebal = balance - amount
            collection.update_one({'user_id': f'{ctx.author.id}'}, {"$set": {'wallet': loosebal}})
            await ctx.send("You didn't win :( You lost the money that you bet.")

    @cog_ext.cog_subcommand(
        base='eco',
        name='leaderboard',
        description='A list of the top 10 richest people',
        guild_ids=guild_ids,
        options=[manage_commands.create_option(
            name='people',
            description='The amount of people to display on the leaderboard.',
            option_type=4,
            required=True
        )]
    )

    async def leaderboard(self, ctx, people: int):

        users = get_bank_data()
        leader_board = {}
        total = []

        for user in users:
            name = int(user)
            total_amount = users[user]["wallet"] + users[user]["bank"]
            leader_board[total_amount] = name
            total.append(total_amount)

        total = sorted(total, reverse=True)


        embed = discord.Embed(title = f"Top {people} Richest People", description='Based on money in wallet and money in bank combined.', color = 0x205675)
        index = 1
        for amount in total:
            id_ = leader_board[amount]
            member = self.bot.get_user(id_)
            name = member.name
            embed.add_field(name = f"{index}. {name}", value = f"{amount}", inline = False)
            if index == people:
                break
            else:
                index += 1
        await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base='eco',
        name='rob',
        description='Rob somebody of their money.',
        guild_ids=guild_ids,
        options=[manage_commands.create_option(
                name='user',
                description='The user you want to rob.',
                option_type=6,
                required=True
            )])
    async def rob(self, ctx, user: discord.Member):
        open_account(ctx.author)
        
        
        authoracct = collection.find_one({'user_id': f'{ctx.author.id}'})
        authorwallet = authoracct['wallet']
        
        
        doc = collection.find_one({'user_id': f'{user.id}'})
        if doc == None:
            await ctx.send('User is not setup')
        elif doc != None:
            victimwallet = doc['wallet']


            if victimwallet < 10:
                await ctx.send(f"To be honest, this {user.name} is broke, you shouldn't rob them.")
                return


            rob_amount = random.randrange(0, 456)
            # make sure not too high
            total_for_robber = rob_amount + authorwallet

            updatedoc = collection.update_one({'user_id': f'{ctx.author.id}'}, {"$set": {'wallet': total_for_robber}})
            newbalforvic = victimwallet - rob_amount

            updateupdoc = collection.update_one({'user_id': f'{user.id}'}, {"$set": {'wallet': newbalforvic}})
            await ctx.send(f"You have succesfully robbed {user.name} of {rob_amount} coins.")



def setup(bot: commands.Bot):
    bot.add_cog(eco(bot))