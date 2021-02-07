import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get

import urllib.request
import urllib.parse
import pandas as pd
import numpy as np
import re
import time

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

current_members = pd.read_csv('./membership-list.csv', index_col=0)
current_members.rename(columns={"Email Address": "email"}, inplace=True)
current_members.drop(current_members[~current_members['email'].str.contains('@')].index, inplace=True)

def searchInMemberShipList(handle):

    if(not re.match('^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$', handle)):
        return (False, 'Email address is not valid.')

    print(current_members.columns)
    
    if(len(current_members.loc[current_members['email']==handle]) != 0):
        print('exists')
        return (True, 'Valid email address.') 
    else: 
        return (False, 'Form not filled in. Please fill in the form.')

@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
        
    print(f'{bot.user} has connected to Discord!')
    print(f'{guild.name}(id: {guild.id})')
    
    memberlist = [member.name for member in guild.members]
    print(f'Guild members: \n - {memberlist}')


@bot.command(name='poll', pass_context=True)
async def poll(ctx, waittime):
    embed = discord.Embed(title = 'This is the question', color = 3553599, description = 'Sample poll')
    react_message = await ctx.send(embed = embed)
    await react_message.add_reaction('👍')
    await react_message.add_reaction('✅')
    time.sleep(float(waittime))

    cache_msg = await ctx.fetch_message(react_message.id) 
    print(cache_msg.reactions)   

    counts = {react.emoji: react.count for react in cache_msg.reactions}
    print(counts)

@bot.command(name='submitsocial', pass_context=True)
async def verify(ctx):
    await ctx.send("Let's go ahead and do some quick verification so I can admit you into the server.")
    await ctx.send("Enter any social media URL")

    def check(m):
        return '@' in m.content
    
    msg = await bot.wait_for("message", check=check)
    await ctx.send("Let me verify that for you")

    url = msg.content

    status, resultMessage = searchInMemberShipList(url)
    if(~status):
        if (resultMessage == 'Email address is not valid'):
            await ctx.send(resultMessage)
        elif (resultMessage == 'Form not filled in. Please fill in the form.'):
            await ctx.send(resultMessage)
        else:
            await ctx.send(resultMessage)
    else:
        try:
            status_code = urllib.request.urlopen(url).getcode()
            valid_page = status_code == 200
            if (valid_page):
                await ctx.send('You have been verified. You will be given member access.')
                member = ctx.message.author
                role = get(member.guild.roles, name='member')
                print(role)
                await member.add_roles(role)

        except Exception as e:
            print(e)
            await ctx.send("I couldn't find an account on that particular page. Let's retry the verification. Call me again using !verify.")
    
@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(f"Hi {member.name}, welcome to GDSC@MMU's Discord Server. We're glad you're here.")

bot.run(TOKEN)

