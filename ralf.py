# import pdb
import os
import re
import time
import sys
import asyncio
import discord
import pyrebase

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

config = {
  "apiKey": os.environ['INTERPOINT_FIREBASE_API_KEY'],
  "authDomain": "interpoint-384c3.firebaseapp.com",
  "databaseURL": "https://interpoint-384c3.firebaseio.com",
  "storageBucket": "interpoint-384c3.appspot.com"
}

firebase = pyrebase.initialize_app(config)
firebase_namespace = os.getenv('FIREBASE_NAMESPACE', default='interpoint-test')
database = firebase.database()

@client.event
async def on_error(_):
  sys.stderr.flush()

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

  if message.content.startswith('?schedule'):
    await evaluate_schedule(message)

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
    author = message.author
    author_roles = list(map(lambda x: x.name, author.roles))

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

      text = message.content.lower()
      text = clear_reclamation_mechs(text)
      mission_numbers = re.findall(r"(?<![a-zA-Z0-9\-])[1-7](?![a-zA-Z0-9\-])", text)
      pilot_code = re.search(r"[a-z0-9]{32}", text)

      if mission_numbers:
        store_user_data(author, {
          "name": author.nick,
          "mention": author.mention,
          "mission_numbers": mission_numbers,
          "pilot_code": pilot_code and pilot_code.group(0),
          "timestamp": int(time.time())
        })
        await asyncio.wait([add_mission_reaction(message, number) for number in mission_numbers])

async def remove_reaction(reaction):
  if reaction.me:
    await reaction.remove(client.user)

async def add_mission_reaction(message, number):
  reaction_dict = { '1': "1️⃣", '2': "2️⃣", '3': "3️⃣", '4': "4️⃣", '5': "5️⃣", '6': "6️⃣", '7': "7️⃣"  }
  await message.add_reaction(reaction_dict.get(number))

async def evaluate_schedule(message):
  if not (message.author.id == 202688077351616512 or message.author.id == 550523153302945792):
    return await message.channel.send("You are not worthy!")

  schedule = [ [ None for y in range( 4 ) ] for x in range( 7 ) ]

  schedule_message = 'Schedule evaluated.\n'
  applicants = database.child(firebase_namespace).child("users").order_by_child("timestamp").get().val()

  scheduled = False
  for key, applicant in applicants.items():
    scheduled = False
    for mission_number in applicant['mission_numbers']:
      if not scheduled:
        for idx, spot in enumerate(schedule[int(mission_number) - 1]):
          if spot == None:
            schedule[int(mission_number) - 1][idx] = applicant
            scheduled = True
            break

  print(schedule, flush=True)

  for idx, mission in enumerate(schedule):
    schedule_message += f"\n\nMission {idx + 1}\n"
    for idx, spot in enumerate(mission):
      schedule_message += str(spot and spot['name'])
      if idx != 3:
        schedule_message += ', '

  await message.channel.send(schedule_message)

def store_user_data(user, data):
  object = database.child(firebase_namespace).child("users").child(user.id).get().val()

  if object:
    if 'timestamp' in object:
      data['timestamp'] = object['timestamp']

  print(data, flush=True)

  database.child(firebase_namespace).child("users").child(user.id).set(data)

def clear_reclamation_mechs(text):
  reclamation_mechs = [
    r"intercorp neo rnd collection \d",
    r"nyx' pirates collection \d",
    r"red hand collection \d",
    r"interpoint security collection \d",
    r"anton industries collection \d",
    r"disciples of seren collection \d",
    r"hayase future systems collection \d",
    r"harmon medical organisation collection \d",
    r"39 thieves collection \d",
    r"calavera's bandits collection \d",
  ]

  for mech_pattern in reclamation_mechs:
    text = re.sub(mech_pattern, 'X', text)

  return text

client.run(os.environ['RALF_JR_DISCORD_TOKEN'])
