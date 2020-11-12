# import pdb
import os
import re
import asyncio
import discord
from firebase import firebase

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

firebase = firebase.FirebaseApplication('https://interpoint-384c3.firebaseio.com', authentication=None)

@client.event
async def on_ready():
  print('ASSUMING DIRECT CONTROL! Taken over {0.user} v2'.format(client))

@client.event
async def on_member_join(member):
  general_channel = discord.utils.get(member.guild.channels, name='interpoint-station') or discord.utils.get(member.guild.channels, name='general')
  example_channel = client.get_channel(734745904468197379)
  announce_channel = client.get_channel(734729551388737560)
  schedule_channel = client.get_channel(734729609182052423)

  message = 'Hey {0.mention}, welcome to Interpoint Station :tm:\n\n' \
    'This is a server for playing pick up games of Lancer RPG.' \
    ' Visit Official Stuff all the way up there for the rundown.\n\n' \
    'If you\'re a trained Lancer and ready to fly, visit {3.mention} and' \
    ' {1.mention} and get your pilot code from COMP/CON ready.' \
    '\n\nIf the schedule is full (check {2.mention} to see if it is)' \
    ' you can still apply for reserves for a chance if a pilot goes AWOL' \
    'or set up a character and join the RP till Sunday when the schedule opens up again.' \
    '\n\nIf you ever need help, just ask any of us, we\'re pretty friendly.' \
    '\n\nWe hope you enjoy your stay at Interpoint Station:tm:'

  await general_channel.send(message.format(member, example_channel, announce_channel, schedule_channel))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.channel.name == 'pilot-application':
    await handle_pilot_application(message)

  if message.content.startswith('?youtube'):
    await message.channel.send('https://www.youtube.com/channel/UCV88ITZdBYnLpRGDFYXymKA')

  if message.content.startswith('?twitter'):
    await message.channel.send('https://twitter.com/InterpointStat1')

  if message.content.startswith('?twitch'):
    await message.channel.send('https://www.twitch.tv/interpointstation')

  if message.content.startswith('?patreon'):
    await message.channel.send('https://www.patreon.com/interpoint')

  if message.content.startswith('?roll20'):
    await message.channel.send('https://app.roll20.net/join/8055988/5rQ7CQ')

  cowboy_content = [
    'cowboy',
    'terminator',
    'high noon'
  ]

  if any(reference in message.content.lower() for reference in cowboy_content):
    await message.add_reaction("<:Cowboy:749333761585578004>")

  cowboy_content = [
    'cube',
    'c.u.b.e',
    'c u b e'
  ]

  if any(reference in message.content.lower() for reference in cowboy_content):
    await message.add_reaction("<:cube:744345789802741900>")

@client.event
async def on_message_edit(_, message):
  await handle_pilot_application(message)

async def handle_pilot_application(message):
  if message.channel.name == 'pilot-application':
    author_roles = list(map(lambda x: x.name, message.author.roles))

    mission_roles = [
      "Mission1 Crew",
      "Mission2 Crew",
      "Mission3 Crew",
      "Mission4 Crew",
      "Mission5 Crew",
      "Mission6 Crew",
      "Mission7 Crew"
    ]

    if set(author_roles) & set(mission_roles):
      await message.add_reaction("\U000023F0") # Alarm clock
    else:
      if message.reactions:
        await asyncio.wait([remove_reaction(reaction) for reaction in message.reactions])

      mission_numbers = re.findall(r"(?<![a-zA-Z0-9\-])[1-7](?![a-zA-Z0-9\-])", message.content.lower())
      if mission_numbers:
        await asyncio.wait([add_mission_reaction(message, number) for number in mission_numbers])

async def remove_reaction(reaction):
  if reaction.me:
    await reaction.remove(client.user)

async def add_mission_reaction(message, number):
  reaction_dict = { '1': "1️⃣", '2': "2️⃣", '3': "3️⃣", '4': "4️⃣", '5': "5️⃣", '6': "6️⃣", '7': "7️⃣"  }
  await message.add_reaction(reaction_dict.get(number))

client.run(os.environ['RALF_JR_DISCORD_TOKEN'])
