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
intents.messages = True
client = discord.Client(intents=intents)

config = {
  "apiKey": os.environ.get('INTERPOINT_FIREBASE_API_KEY'),
  "authDomain": "interpoint-384c3.firebaseapp.com",
  "databaseURL": "https://interpoint-384c3.firebaseio.com",
  "storageBucket": "interpoint-384c3.appspot.com"
}

IS_DEV_ENV = config['apiKey'] is None

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

cooldown_roles = [
  "Cooldown",
  "Cooldown Week 1 (of 2)",
  "Cooldown Week 2 (of 2)",
  "Cooldown Week 3 (of 3)",
]

@client.event
async def on_ready():
  print('ASSUMING DIRECT CONTROL! Taken over {0.user} v2'.format(client))

@client.event
async def on_raw_reaction_add(payload):
  if payload.emoji.name == '✅':
    channel = client.get_channel(payload.channel_id)
    if channel.id == 780346906509312060:
      rp_role = discord.utils.get(payload.member.guild.roles, name='Role-Player')
      await payload.member.add_roles(rp_role, reason='Agreed to RP Etiquette')
    if channel.id == 797929892078813184:
      sg_role = discord.utils.get(payload.member.guild.roles, name='Side Game Seeker')
      await payload.member.add_roles(sg_role, reason='Looking for Side Games')

@client.event
async def on_member_join(member):
  general_channel = discord.utils.get(member.guild.channels, name='interpoint-station') or discord.utils.get(member.guild.channels, name='general')
  announce_channel = client.get_channel(734729551388737560)
  rp_channel = client.get_channel(780346906509312060)
  what_channel = client.get_channel(762884231898071041)
  rules_channel = client.get_channel(734744137815031809)
  side_channel = client.get_channel(797929892078813184)

  message = 'Hey {0.mention}, welcome to Interpoint Station :tm:\n\n' \
    'This is a server for playing pick up games of Lancer RPG. Visit {3.mention} for a quick rundown, then check out {4.mention} for instructions on how to play in official Interpoint games.' \
    '\n\nIn addition to the weekly main missions, members of the Interpoint community sometimes run side games. Visit {5.mention} to learn more about how these games work and sign up for alerts when they happen.' \
    '\n\nIf you want to get involved in the text-based RP in this server, head down to {2.mention} and follow the rules to unlock the RP channels.' \
    '\n\nIf you ever need help, just ask any of us! We\'re pretty friendly.' \
    '\n\nWe hope you enjoy your stay at Interpoint Station:tm:'

  await general_channel.send(message.format(member, announce_channel, rp_channel, what_channel, rules_channel, side_channel))

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

  if message.content.startswith('?reset-weight'):
    await reset_weight(message)

  if message.content.startswith('?hard-reset-weight'):
    await hard_reset_weight(message)

  if message.content.startswith('?increase-weight'):
    await increase_weight(message)

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
    await message.channel.send('https://app.roll20.net/join/9499499/icSkKQ')

  if message.content.startswith('?homebrew'):
    await message.channel.send('https://interpoint-station.itch.io/intercorp')

  if message.content.startswith('?random-build'):
    await get_random_build(message)

  if message.content.startswith('?random-frame'):
    await get_random_mech(message)

  if message.content.startswith('?random-mech'):
    await get_random_mech(message)

  if message.content.startswith('?random-trait'):
    await get_random_trait(message)

  if message.content.startswith('?random-cp'):
    await get_random_cp(message)

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
async def on_raw_message_edit(payload):
  channel = client.get_channel(payload.channel_id)
  message = await channel.fetch_message(payload.message_id)

  await handle_pilot_application(message)

async def handle_pilot_application(message):
  if message.channel.name == 'pilot-application':
    author = message.author
    if author.id == 550523153302945792:
      return
    author_roles = list(map(lambda x: x.name, author.roles))

    if (set(author_roles) & set(mission_roles)) or (set(author_roles) & set(cooldown_roles)):
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
          "weight": 0.1,
          "name": author.nick or author.name,
          "mention": author.mention,
          "mission_numbers": mission_numbers,
          "pilot_code": pilot_code and pilot_code.group(0),
          "mech_token": mech_token,
          "author_roles": author_roles,
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

  # Remove applications that are older than 6 days
  cutoff = datetime.datetime.now()
  cutoff = cutoff - datetime.timedelta(days=6)
  cutoff_epoch = cutoff.timestamp() * 1000

  for key in list(applicants.keys()):
    if applicants[key]['timestamp'] < cutoff_epoch:
      del applicants[key]

  if message.content.startswith('?random-schedule '):
    cutoff_role = re.sub(re.escape('?random-schedule '), '', message.content)
    for key in list(applicants.keys()):
      if cutoff_role not in applicants[key]['author_roles']:
        del applicants[key]

  applicant_ids = []
  applicant_weights = []

  for id, applicant in applicants.items():
    applicant_ids.append(id)
    weight = applicant['weight']
    applicant_weights.append(weight)

  total_weight = sum(applicant_weights)
  applicant_weights = list(map(lambda x: (x / total_weight), applicant_weights))

  lucky_draw = choice(applicant_ids, len(applicant_ids), replace=False, p=applicant_weights)

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
  object = database.child(firebase_namespace).child("users").child(user.id).get().val()

  if object:
    if 'weight' in object:
      data['weight'] = object['weight']

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

def get_applicants():
  if IS_DEV_ENV:
    QAZZ_ID = 169544927351537664
    return {
      f"{QAZZ_ID}": {
        'author_roles': ['@everyone'],
        'id': f'{QAZZ_ID}',
        'mech_token': '#1',
        'mention': f"<@!{QAZZ_ID}>",
        'mission_numbers': ['1'],
        'name': 'Test',
        'pilot_code': '1234',
        'weight': 1,
        'timestamp': 1234567890
      }
    }

  users_table = database.child(firebase_namespace).child("users")
  applicants = users_table.get().val()
  return applicants
async def reset_weight(message):
  author = message.author
  author_roles = list(map(lambda x: x.name, author.roles))
  if not (message.author.id == 202688077351616512 or message.author.id == 550523153302945792 or 'Moderator' in author_roles):
    return await message.channel.send("You are not worthy!")

  applicants = database.child(firebase_namespace).child("users").get().val()

  # Remove applications that are older than 30 days
  cutoff = datetime.datetime.now()
  cutoff = cutoff - datetime.timedelta(days=30)
  cutoff_epoch = cutoff.timestamp() * 1000

  for key in list(applicants.keys()):
    if applicants[key]['timestamp'] < cutoff_epoch:
      del applicants[key]

  # Only keep people on cooldown and in missions
  for key in list(applicants.keys()):
    applicant_roles = await get_user_roles(author.guild, key)
    if applicant_roles:
      if not ((set(applicant_roles) & set(mission_roles)) or (set(applicant_roles) & set(cooldown_roles))):
        del applicants[key]
    else:
      del applicants[key]

  print('Resetting', flush=True)
  for key in list(applicants.keys()):
    print(applicants[key]['name'], flush=True)
    database.child(firebase_namespace).child("users").child(key).child('weight').set(0.1)

  await message.channel.send('Weight reset')

async def hard_reset_weight(message):
  author = message.author
  author_roles = list(map(lambda x: x.name, author.roles))
  if not (message.author.id == 202688077351616512 or message.author.id == 550523153302945792 or 'Moderator' in author_roles):
    return await message.channel.send("You are not worthy!")

  applicants = database.child(firebase_namespace).child("users").get().val()

  print('Resetting', flush=True)
  for key in list(applicants.keys()):
    print(applicants[key]['name'], flush=True)
    database.child(firebase_namespace).child("users").child(key).child('weight').set(0.1)

  await message.channel.send('Weight hard reset')

async def increase_weight(message):
  author = message.author
  author_roles = list(map(lambda x: x.name, author.roles))
  if not (message.author.id == 202688077351616512 or message.author.id == 550523153302945792 or 'Moderator' in author_roles):
    return await message.channel.send("You are not worthy!")

  applicants = database.child(firebase_namespace).child("users").get().val()

  # Remove applications that are older than 9 days
  cutoff = datetime.datetime.now()
  cutoff = cutoff - datetime.timedelta(days=9)
  cutoff_epoch = cutoff.timestamp() * 1000

  for key in list(applicants.keys()):
    if applicants[key]['timestamp'] < cutoff_epoch:
      del applicants[key]

  # Remove people on cooldown and in missions
  for key in list(applicants.keys()):
    applicant_roles = await get_user_roles(author.guild, key)
    if applicant_roles:
      if (set(applicant_roles) & set(mission_roles)) or (set(applicant_roles) & set(cooldown_roles)):
        del applicants[key]
    else:
      del applicants[key]

  print('Increasing', flush=True)
  for key in list(applicants.keys()):
    print(applicants[key]['name'], flush=True)
    database.child(firebase_namespace).child("users").child(key).child('weight').set(applicants[key]['weight'] * 2)

  await message.channel.send('Weight increased')

async def get_user_roles(guild, user_id):
  try:
    member = await guild.fetch_member(user_id)
    if member:
      return list(map(lambda x: x.name, member.roles))
    else:
      return None
  except:
    return None

async def get_random_build(message):
  build_message = ''
  build_message += random_mech()
  build_message += '\n\n'
  build_message += random_trait()
  build_message += '\n'
  build_message += random_trait()
  build_message += '\n'
  build_message += random_trait()
  build_message += '\n\n'
  build_message += random_cp()

  return await message.channel.send(build_message)

async def get_random_mech(message):
  return await message.channel.send(random_mech())

def random_mech():
  mechs = ["Everest", "Sagarmatha", "Blackbeard", "Drake", "Lancaster", "Nelson", "Raleigh", "Tortuga", "Vlad", "Caliban", "Zheng", "Kidd", "Black Witch", "Death's Head", "Dusk Wing", "Metal Mark", "Monarch", "Mourning Cloak", "Swallowtail", "Ranger Swallowtail", "Atlas", "Balor", "Goblin", "Gorgon", "Hydra", "Manticore", "Minotaur", "Pegasus", "Kobold", "Lich", "Barbarossa", "Ghengis", "Ghengis Mk1", "Iskander", "Napoleon", "Saladin", "Sherman", "Tokugawa", "Enkidu", "Sunzi"]
  mech = choice(mechs)
  return mech

async def get_random_trait(message):
  return await message.channel.send(random_trait())

def random_trait():
  traits = [ "Iniative Everest", "Replacable Parts Everest", "Guardian Sagmartha", "Heroism Sagmartha", "Grapple Cable Black Beard", "Lock Kill Sub System Black Beard", "Exposed Reactor Black Beard", "Wrecking Ball Caliban", "Pursue Prey Caliban", "Slam Caliban", "Weak Computer Caliban", "Heavy Frame Drake", "Blast Plating Drake", "Slow Drake", "Guardian Drake", "Reroute Power + Recycle Kidd Lose 1 Trait or Re-Roll this Trait", "Rapid Deployment Kidd", "Insulated Lancaster", "Combat Repair Lancaster", "Redundant System Lancaster", "Momentum Nelson", "Skirmisher Nelson", "Full Metal Jacket Raleigh", "Shielded Magazines Raleigh", "Sentinel Tortuga", "Guardian Tortuga", "Dismemberment Vlad", "Shrike Armor Vlad", "Giant Killer Atlas", "Jäger Dodge Atlas", "Finishing Blow Atlas", "Exposed Reactor Atlas", "Repulser Field Black Witch", "Mag Parry Black Witch", "Neuro Link Deaths Head", "Perfected Targeting Deaths Head", "Manouverability Jets Duskwing", "Harlequin Cloak Duskwing", "Fragile Duskwing", "Flash Cloak Metal Mark", "Carapace Adaption Metal Mark", "Avenger Silos Monarch", "Seeking Payload Monarch", "Hunter Mourning Cloak", "Biotic Components Mourning Cloak", "Integrated Cloak Swallowtail", "Prophetic Scanners Swallowtail", "Scout Battlefield Ranger Swallowtail", "Invigorating Scanners Ranger Swallowtail", "Weathering Ranger Swallowtail", "Self Perpetuating Balor", "Scouring Swarm Balor", "Regenerator Balor", "Liturgycode Goblin", "Reactive Code Goblin", "Fragile Goblin", "Metastatic Paralysis Gorgon", "Gaze Gorgon", "Guardian Gorgon", "System Link Hydra", "Shepherd Field Hydra", "Mimic Carapace Kobold", "Slag Spray Kobold", "Exposed Reactor Kobold", "Soul Vessel Lich", "Immortal Lich (Return to Wreckage instead of Soul Vessel)", "Slag Carapace Manticore", "Unstable System Manticore", "Castigate the Enemies Manticore", "Invert Cockpit Minotaur", "Internal Metafold Minotaur", "Localised Maze Minotaur", "By the Way I know every Pegasus", "Heavy Frame Barbarossa", "Pressure Plating Barbarossa", "Guardian Barbarossa", "Slow Barbarossa", "Insulated Ghengis", "Emergency Vent Ghengis", "Weak Computer Ghengis Mk1", "Insulated Ghengis Mk1", "TBK Munitions Ghengis Mk1", "Assault Launcher Iskander", "Mine Deployer Iskander", "Skeleton Key Iskander", "Heavy Shielding Napoleon", "Flash Aegis Napoleon", "Reinforced Frame Saladin", "Guardian Saladin", "Warp Shield Saladin", "Superior Reactor Sherman", "Marthur Stop Sherman", "Vent Heat Sherman", "Safe Harbor Sunzi", "Anchor Sunzi", "Slip Sunzi", "Limit Break Tokugawa", "Plasma Sheath Tokugawa", "Primal Fury + Talons Enkidu", "All Fours Enkidu", "Brute Strength Enkidu", "Bloodsense Enkidu" ]
  trait = choice(traits)
  return trait

async def get_random_cp(message):
  return await message.channel.send(random_cp())

def random_cp():
  cps = [ "Hyper Spec Fuel Injector Everest", "Raise the Banner Sagarmatha", "Omni Harpoon Blackbeard", "Fortress Protocol Drake", "Latch Drone + Supercharger Lancaster", "Engage Drive + Skirmisher Nelson Lose 1 Trait or Re-Roll this CP", "Mjolnir Cannon + Thunder God Raleigh", "Hyper Reflex Mode Tortuga", "Tormentor Spikes + Shrike Armor Vlad Lose 1 Trait or Re-Roll this CP", "Flayer Shotgun + Equip Autochoke Caliban", "Xiaoli's Tenacity + Xiaoli's Ingenuity Zheng", "Jolly Roger + Skull and Bones Kidd", "Mag Field Black Witch", "Neural Shunt Death's Head", "Hall of Mirrors Dusk Wing", "Tactical Cloak Metal Mark", "Divine Punishment Monarch", "Blinkspace Jump + Stabilize Singularity Mourning Cloak", "Prophetic Interjection Swallowtail", "Grounded + Guerilla Warfare Ranger Swallowtail", "Final Hunt Atlas", "Scouring Swarm + Regeneration + Hive Frenzy Balor Lose 2 Traits or Re-Roll this CP", "Symbiosis Goblin", "Extrude Basilisk Gorgon", "Orochi Drones+Full Deployment Hydra", "Charged Exoskeleton + Destruction of the temple Manticore", "Metafold Maze + Maze Minotaur", "Ushabti Omnigun + Unshackle Ushabti Pegasus", "Terraform Kobold", "Glitch Time Lich", "Apocalypse Rail + Charge Rail Barbarossa", "Expose Powercells Ghengis", "Furiosa + A Pleasure to Burn Ghengis Mk1", "Death Cloud Iskander", "Trueblack Aegis Napoleon", "Tachyon Shield Saladin", "ZF4 Solidcore + Coreburn Protocol Sherman", "Overclock + Radiance Tokugawa", "Crush Limiter Enkidu", "Blink Anchor + Art of War Sunzi" ]
  cp = choice(cps)
  return cp

client.run(os.environ['RALF_JR_DISCORD_TOKEN'])
