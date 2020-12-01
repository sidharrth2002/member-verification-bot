import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get

import urllib.request
import urllib.parse

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
        
    print(f'{bot.user} has connected to Discord!')
    print(f'{guild.name}(id: {guild.id})')
    
    memberlist = [member.name for member in guild.members]
    print(f'Guild members: \n - {memberlist}')


@bot.command(name='verify', pass_context=True)
async def verify(ctx):
    await ctx.send("Let's go ahead and do some quick verification so I can admit you into the server.")
    await ctx.send("Enter any social media URL")

    def check(m):
        return m.content[0:5] == 'https' or m.content[0:4] == 'http'
    
    msg = await bot.wait_for("message", check=check)
    await ctx.send("Let me verify that for you")

    url = msg.content
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