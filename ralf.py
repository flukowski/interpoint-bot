# import pdb
import os
import re
import datetime
import asyncio
import discord
import pyrebase
import collections
import numpy
from numpy.random import choice

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

mission_roles = [
  "Mission1 Crew",
  "Mission2 Crew",
  "Mission3 Crew",
  "Mission4 Crew",
  "Mission5 Crew",
  "Mission6 Crew",
  "Mission7 Crew"
]

@client.event
async def on_ready():
  print('ASSUMING DIRECT CONTROL! Taken over {0.user} v2'.format(client))

@client.event
async def on_raw_reaction_add(payload):
  if payload.emoji.name == '✅':
    channel = client.get_channel(payload.channel_id)
    if channel.name == 'rp-etiquette':
      rp_role = discord.utils.get(payload.member.guild.roles, name='Role-Player')
      await payload.member.add_roles(rp_role, reason='Agreed to RP Etiquette')

@client.event
async def on_member_join(member):
  general_channel = discord.utils.get(member.guild.channels, name='interpoint-station') or discord.utils.get(member.guild.channels, name='general')
  announce_channel = client.get_channel(734729551388737560)

  message = 'Hey {0.mention}, welcome to Interpoint Station :tm:\n\n' \
    'This is a server for playing pick up games of Lancer RPG. Visit Official Stuff all the way up there for the rundown.' \
    '\n\nGo right ahead and make a LL0 character for our games utilizing Comp/Con app and its cloud feature. https://compcon.app/#/ Then you can apply using the generated pilot code!' \
    '\n\nApplications open on Sundays for the following week, I generally run 7 games a week which means that there are 28 spots available making it 112 a month.' \
    '\n\nIf the schedule is full (check {1.mention} to see if it is) you can still apply for reserves for a chance if a pilot goes AWOL or set up a character and join the RP till Sunday when the schedule opens up again.' \
    '\n\nIf you ever need help, just ask any of us, we\'re pretty friendly.' \
    '\n\nWe hope you enjoy your stay at Interpoint Station:tm:'

  await general_channel.send(message.format(member, announce_channel))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.channel.name == 'pilot-application':
    await handle_pilot_application(message)

  if message.content.startswith('?schedule'):
    await evaluate_schedule_v2(message)

  if message.content.startswith('?random-schedule'):
    await evaluate_schedule_random(message)

  if message.content.startswith('?codes'):
    await get_codes(message)

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

    if set(author_roles) & set(mission_roles):
      await message.add_reaction("\U000023F0") # Alarm clock
    else:
      if message.reactions:
        await asyncio.wait([remove_reaction(reaction) for reaction in message.reactions])

      text = message.content.lower()
      mech_token, text = get_mech_token(text)
      mission_numbers = re.findall(r"(?<![a-zA-Z0-9\-])[1-7](?![a-zA-Z0-9\-])", text)
      pilot_code = re.search(r"[a-z0-9]{32}", text)

      if mission_numbers:
        store_user_data(author, {
          "id": author.id,
          "weight": 1,
          "name": author.nick or author.name,
          "mention": author.mention,
          "mission_numbers": mission_numbers,
          "pilot_code": pilot_code and pilot_code.group(0),
          "mech_token": mech_token,
          "timestamp": message.created_at.timestamp() * 1000
        })
        await asyncio.wait([add_mission_reaction(message, number) for number in mission_numbers])

async def remove_reaction(reaction):
  if reaction.me:
    await reaction.remove(client.user)

async def add_mission_reaction(message, number):
  reaction_dict = { '1': "1️⃣", '2': "2️⃣", '3': "3️⃣", '4': "4️⃣", '5': "5️⃣", '6': "6️⃣", '7': "7️⃣"  }
  await message.add_reaction(reaction_dict.get(number))

async def evaluate_schedule_random(message):
  if not (message.author.id == 202688077351616512 or message.author.id == 550523153302945792):
    return await message.channel.send("You are not worthy!")

  applicants = database.child(firebase_namespace).child("users").get().val()

  # Remove applications that are older than 2 days
  cutoff = datetime.datetime.now()
  cutoff = cutoff - datetime.timedelta(days=2)
  cutoff_epoch = cutoff.timestamp() * 1000

  for key in list(applicants.keys()):
    if applicants[key]['timestamp'] < cutoff_epoch:
      del applicants[key]

  applicant_ids = []

  for id, applicant in applicants.items():
    applicant_ids.append(id)

  lucky_draw = choice(applicant_ids, 36, replace=False)

  final_applicants = collections.OrderedDict()

  for key in lucky_draw:
    final_applicants[key] = applicants[key]

  print(final_applicants)

  schedule = calculate_schedule(final_applicants)

  schedule_message = 'Random Schedule evaluated.\n'

  for idx, mission in enumerate(schedule):
    schedule_message += f"\n\nMission {idx + 1}\n"
    for idx, spot in enumerate(mission):
      schedule_message += str(spot and spot['mention'])
      if idx != 3:
        schedule_message += ', '

  await message.channel.send(schedule_message)

async def evaluate_schedule_v2(message):
  if not (message.author.id == 202688077351616512 or message.author.id == 550523153302945792):
    return await message.channel.send("You are not worthy!")

  applicants = database.child(firebase_namespace).child("users").order_by_child("timestamp").get().val()

  schedule = calculate_schedule(applicants)

  schedule_message = 'Schedule evaluated.\n'

  for idx, mission in enumerate(schedule):
    schedule_message += f"\n\nMission {idx + 1}\n"
    for idx, spot in enumerate(mission):
      schedule_message += str(spot and spot['mention'])
      if idx != 3:
        schedule_message += ', '

  await message.channel.send(schedule_message)

def calculate_schedule(applicants):
  schedule = [ [ None for y in range( 4 ) ] for x in range( 7 ) ]
  filled_count = 0
  scheduled = False

  for key, applicant in applicants.items():
    if filled_count == 28:
      break
    scheduled = False
    print(applicant['name'], flush=True)

    if len(applicant['mission_numbers']) == 1:
      single_mission_number = applicant['mission_numbers'][0]
      for idx, spot in enumerate(schedule[int(single_mission_number) - 1]):
        if spot == None:
          schedule[int(single_mission_number) - 1][idx] = applicant
          scheduled = True
          print('Gets into {0}'.format(single_mission_number), flush=True)
          filled_count += 1
          break
      if not scheduled:
        rescheduled = False
        for idx, spot in enumerate(schedule[int(single_mission_number) - 1]):
          if rescheduled:
            break
          other_numbers = None
          for mission_number in spot['mission_numbers']:
            other_numbers = [x for x in spot['mission_numbers'] if x != single_mission_number]
          if other_numbers:
            for mission_number in other_numbers:
              for other_idx, other_spot in enumerate(schedule[int(mission_number) - 1]):
                if other_spot == None:
                  schedule[int(mission_number) - 1][other_idx] = spot
                  rescheduled = True
                  print('Pushes {0} to {1}'.format(spot['name'], mission_number), flush=True)
                  break
              if rescheduled:
                schedule[int(single_mission_number) - 1][idx] = applicant
                scheduled = True
                print('Gets into {0}'.format(single_mission_number), flush=True)
                filled_count += 1
                break
    else:
      for mission_number in applicant['mission_numbers']:
        if not scheduled:
          for idx, spot in enumerate(schedule[int(mission_number) - 1]):
            if spot == None:
              schedule[int(mission_number) - 1][idx] = applicant
              scheduled = True
              print('Gets into {0}'.format(mission_number), flush=True)
              filled_count += 1
              break

  print(schedule, flush=True)

  return schedule

def store_user_data(user, data):
  # For normal schedule we need maintain the first timestamp in the week
  # object = database.child(firebase_namespace).child("users").child(user.id).get().val()

  # if object:
  #   if 'timestamp' in object:
  #     data['timestamp'] = object['timestamp']

  print(data, flush=True)

  database.child(firebase_namespace).child("users").child(user.id).set(data)

def get_mech_token(text):
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
    r"angel vermillion collection \d",
    r"(token|interest) #?\d{1,2} ?[ab]", # Interest token numbers
    r"(token|interest) .+ ?[ab]",
    r"#\d{1,2} ?[ab]",
    r"#\d{1,2}",
  ]

  token = ''

  for mech_pattern in reclamation_mechs:
    search_result = re.search(mech_pattern, text)
    if search_result:
      token += search_result.group(0)
      token += ' '
      text = re.sub(mech_pattern, 'X', text)

  return (token, text)

async def get_codes(message):
  if not (message.author.id == 202688077351616512 or message.author.id == 550523153302945792):
    return await message.channel.send("You are not worthy!")

  applicants = database.child(firebase_namespace).child("users").get().val()

  codes_message = ''

  for role in message.author.guild.roles:
    if role.name in mission_roles:
      codes_message += '\n\n'
      codes_message += role.name
      codes_message += '\n'
      for member in role.members:
        try:
          codes_message += applicants[str(member.id)]['mention']
          codes_message += '\n'
          codes_message += applicants[str(member.id)]['pilot_code']
          codes_message += '\n'
          codes_message += applicants[str(member.id)]['mech_token']
          codes_message += '\n'
        except KeyError:
          continue

  await message.channel.send(codes_message)

client.run(os.environ['RALF_JR_DISCORD_TOKEN'])
