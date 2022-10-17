import os
import re
import datetime
import asyncio
import discord
import pyrebase
import collections

from discord import Role
from numpy.random import choice

from generation import (
    get_random_build,
    get_random_mech,
    get_random_trait,
    get_random_cp,
)
from permissions import admin_only, moderator_only, QAZZ_ID

intents = discord.Intents.default()
intents.members = True
intents.messages = True
client = discord.Client(intents=intents)

config = {
    "apiKey": os.environ.get("INTERPOINT_FIREBASE_API_KEY"),
    "authDomain": "interpoint-384c3.firebaseapp.com",
    "databaseURL": "https://interpoint-384c3.firebaseio.com",
    "storageBucket": "interpoint-384c3.appspot.com",
}

IS_DEV_ENV = config["apiKey"] is None

firebase = pyrebase.initialize_app(config)
firebase_namespace = os.getenv("FIREBASE_NAMESPACE", default="interpoint-test")
database = firebase.database()

mission_roles = [
    "Mission1 Crew",
    "Mission2 Crew",
    "Mission3 Crew",
    "Mission4 Crew",
    "Mission5 Crew",
    "Mission6 Crew",
    "Mission7 Crew",
]

cooldown_roles = [
    "Cooldown",
    "Cooldown Week 1 (of 2)",
    "Cooldown Week 2 (of 2)",
    "Cooldown Week 3 (of 3)",
]


class Channel:
    announcements = client.get_channel(734729551388737560)
    rp = client.get_channel(780346906509312060)
    what = client.get_channel(762884231898071041)
    rules = client.get_channel(734744137815031809)
    side = client.get_channel(797929892078813184)


@client.event
async def on_ready():
    print(f"ASSUMING DIRECT CONTROL! Taken over {client.user} v2")


@client.event
async def on_raw_reaction_add(payload):
    if payload.emoji.name == "✅":
        channel = client.get_channel(payload.channel_id)
        if channel.id == Channel.rp.id:
            rp_role = discord.utils.get(payload.member.guild.roles, name="Role-Player")
            await payload.member.add_roles(rp_role, reason="Agreed to RP Etiquette")
        if channel.id == Channel.side.id:
            sg_role = discord.utils.get(
                payload.member.guild.roles, name="Side Game Seeker"
            )
            await payload.member.add_roles(sg_role, reason="Looking for Side Games")


@client.event
async def on_member_join(member):
    general_channel = discord.utils.get(
        member.guild.channels, name="interpoint-station"
    ) or discord.utils.get(member.guild.channels, name="general")

    message = f"""\
Hey {member}, welcome to Interpoint Station :tm:
  
This is a server for playing pick up games of Lancer RPG. Visit {Channel.what} for a quick rundown, then check out {Channel.rules} for instructions on how to play in official Interpoint games.
In addition to the weekly main missions, members of the Interpoint community sometimes run side games. Visit {Channel.side} to learn more about how these games work and sign up for alerts when they happen.

If you want to get involved in the text-based RP in this server, head down to {Channel.rp} and follow the rules to unlock the RP channels.

If you ever need help, just ask any of us! We're pretty friendly.

We hope you enjoy your stay at Interpoint Station:tm:"""

    await general_channel.send(message)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.name == "pilot-application":
        await handle_pilot_application(message)

    if message.content.startswith("?schedule"):
        await evaluate_schedule_v2(message)

    if message.content.startswith("?random-schedule"):
        await evaluate_schedule_random(message)

    if message.content.startswith("?reset-weight"):
        await reset_weight(message)

    if message.content.startswith("?hard-reset-weight"):
        await hard_reset_weight(message)

    if message.content.startswith("?increase-weight"):
        await increase_weight(message)

    if message.content.startswith("?codes"):
        await get_codes(message)

    if message.content.startswith("?mission-to-cooldown"):
        await move_in_mission_to_on_cooldown(message)

    if message.content.startswith("?weekly-cooldowns"):
        await update_weekly_cooldowns(message)

    if message.content.startswith("?youtube"):
        await message.channel.send(
            "https://www.youtube.com/channel/UCV88ITZdBYnLpRGDFYXymKA"
        )

    if message.content.startswith("?twitter"):
        await message.channel.send("https://twitter.com/InterpointStat1")

    if message.content.startswith("?twitch"):
        await message.channel.send("https://www.twitch.tv/interpointstation")

    if message.content.startswith("?patreon"):
        await message.channel.send("https://www.patreon.com/interpoint")

    if message.content.startswith("?roll20"):
        await message.channel.send("https://app.roll20.net/join/9499499/icSkKQ")

    if message.content.startswith("?homebrew"):
        await message.channel.send("https://interpoint-station.itch.io/intercorp")

    if message.content.startswith("?random-build"):
        await get_random_build(message)

    if message.content.startswith("?random-frame"):
        await get_random_mech(message)

    if message.content.startswith("?random-mech"):
        await get_random_mech(message)

    if message.content.startswith("?random-trait"):
        await get_random_trait(message)

    if message.content.startswith("?random-cp"):
        await get_random_cp(message)

    cowboy_content = ["cowboy", "terminator", "high noon"]

    if any(reference in message.content.lower() for reference in cowboy_content):
        await message.add_reaction("<:Cowboy:749333761585578004>")

    cowboy_content = ["cube", "c.u.b.e", "c u b e"]

    if any(reference in message.content.lower() for reference in cowboy_content):
        await message.add_reaction("<:cube:744345789802741900>")


@client.event
async def on_raw_message_edit(payload):
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)

    await handle_pilot_application(message)


async def handle_pilot_application(message):
    if message.channel.name == "pilot-application":
        author = message.author
        if author.id == 550523153302945792:
            return
        author_roles = list(map(lambda x: x.name, author.roles))

        if (set(author_roles) & set(mission_roles)) or (
            set(author_roles) & set(cooldown_roles)
        ):
            await message.add_reaction("\U000023F0")  # Alarm clock
        else:
            if message.reactions:
                await asyncio.wait(
                    [remove_reaction(reaction) for reaction in message.reactions]
                )

            text = message.content.lower()
            mech_token, text = get_mech_token(text)
            mission_numbers = re.findall(
                r"(?<![a-zA-Z0-9\-])[1-7](?![a-zA-Z0-9\-])", text
            )
            pilot_code = re.search(r"[a-z0-9]{32}", text)

            if mission_numbers:
                store_user_data(
                    author,
                    {
                        "id": author.id,
                        "weight": 0.1,
                        "name": author.nick or author.name,
                        "mention": author.mention,
                        "mission_numbers": mission_numbers,
                        "pilot_code": pilot_code and pilot_code.group(0),
                        "mech_token": mech_token,
                        "author_roles": author_roles,
                        "timestamp": message.created_at.timestamp() * 1000,
                    },
                )
                await asyncio.wait(
                    [
                        add_mission_reaction(message, number)
                        for number in mission_numbers
                    ]
                )


async def remove_reaction(reaction):
    if reaction.me:
        await reaction.remove(client.user)


async def add_mission_reaction(message, number):
    reaction_dict = {
        "1": "1️⃣",
        "2": "2️⃣",
        "3": "3️⃣",
        "4": "4️⃣",
        "5": "5️⃣",
        "6": "6️⃣",
        "7": "7️⃣",
    }
    await message.add_reaction(reaction_dict.get(number))


@admin_only
async def evaluate_schedule_random(message):
    applicants = database.child(firebase_namespace).child("users").get().val()

    # Remove applications that are older than 6 days
    cutoff = datetime.datetime.now()
    cutoff = cutoff - datetime.timedelta(days=6)
    cutoff_epoch = cutoff.timestamp() * 1000

    for key in list(applicants.keys()):
        if applicants[key]["timestamp"] < cutoff_epoch:
            del applicants[key]

    if message.content.startswith("?random-schedule "):
        cutoff_role = re.sub(re.escape("?random-schedule "), "", message.content)
        for key in list(applicants.keys()):
            if cutoff_role not in applicants[key]["author_roles"]:
                del applicants[key]

    applicant_ids = []
    applicant_weights = []

    for applicant_id, applicant in applicants.items():
        applicant_ids.append(applicant_id)
        weight = applicant["weight"]
        applicant_weights.append(weight)

    total_weight = sum(applicant_weights)
    applicant_weights = list(map(lambda x: (x / total_weight), applicant_weights))

    lucky_draw = choice(
        applicant_ids, len(applicant_ids), replace=False, p=applicant_weights
    )

    final_applicants = collections.OrderedDict()

    for key in lucky_draw:
        final_applicants[key] = applicants[key]

    print(final_applicants)

    schedule = calculate_schedule(final_applicants)
    schedule_message = f"Random Schedule evaluated.\n{_make_schedule_message(schedule)}"

    await message.channel.send(schedule_message)


@admin_only
async def evaluate_schedule_v2(message):
    applicants = (
        database.child(firebase_namespace)
        .child("users")
        .order_by_child("timestamp")
        .get()
        .val()
    )

    schedule = calculate_schedule(applicants)

    schedule_message = f"Schedule evaluated.\n{_make_schedule_message(schedule)}"
    await message.channel.send(schedule_message)


def _make_schedule_message(schedule):
    schedule_message = ""
    for mission_idx, mission in enumerate(schedule):
        schedule_message += f"\n\nMission {mission_idx + 1}\n"
        for spot_idx, spot in enumerate(mission):
            schedule_message += str(spot and spot["mention"])
            if spot_idx != 3:
                schedule_message += ", "
    return schedule_message


def calculate_schedule(applicants):
    schedule = [[None for _y in range(4)] for _x in range(7)]
    filled_count = 0
    scheduled = False

    for key, applicant in applicants.items():
        if filled_count == 28:
            break
        scheduled = False
        print(applicant["name"], flush=True)

        if len(applicant["mission_numbers"]) == 1:
            single_mission_number = applicant["mission_numbers"][0]
            for idx, spot in enumerate(schedule[int(single_mission_number) - 1]):
                if spot is None:
                    schedule[int(single_mission_number) - 1][idx] = applicant
                    scheduled = True
                    print(f"Gets into {single_mission_number}", flush=True)
                    filled_count += 1
                    break
            if not scheduled:
                rescheduled = False
                for idx, spot in enumerate(schedule[int(single_mission_number) - 1]):
                    if rescheduled:
                        break
                    other_numbers = None
                    for _mission_number in spot["mission_numbers"]:
                        other_numbers = [
                            x
                            for x in spot["mission_numbers"]
                            if x != single_mission_number
                        ]
                    if other_numbers:
                        for mission_number in other_numbers:
                            for other_idx, other_spot in enumerate(
                                schedule[int(mission_number) - 1]
                            ):
                                if other_spot is None:
                                    schedule[int(mission_number) - 1][other_idx] = spot
                                    rescheduled = True
                                    print(
                                        f"Pushes {spot['name']} to {mission_number}",
                                        flush=True,
                                    )
                                    break
                            if rescheduled:
                                schedule[int(single_mission_number) - 1][
                                    idx
                                ] = applicant
                                scheduled = True
                                print(f"Gets into {single_mission_number}", flush=True)
                                filled_count += 1
                                break
        else:
            for mission_number in applicant["mission_numbers"]:
                if not scheduled:
                    for idx, spot in enumerate(schedule[int(mission_number) - 1]):
                        if spot is None:
                            schedule[int(mission_number) - 1][idx] = applicant
                            scheduled = True
                            print(f"Gets into {mission_number}", flush=True)
                            filled_count += 1
                            break

    print(schedule, flush=True)

    return schedule


def store_user_data(user, data):
    user_object = (
        database.child(firebase_namespace).child("users").child(user.id).get().val()
    )

    if user_object:
        if "weight" in user_object:
            data["weight"] = user_object["weight"]

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
        r"angel vermilion collection \d",
        r"(token|interest) #?\d{1,2} ?[ab]",  # Interest token numbers
        r"(token|interest) .+ ?[ab]",
        r"#\d{1,2} ?[ab]",
        r"#\d{1,2}",
    ]

    token = ""

    for mech_pattern in reclamation_mechs:
        search_result = re.search(mech_pattern, text)
        if search_result:
            token += search_result.group(0)
            token += " "
            text = re.sub(mech_pattern, "X", text)

    return token, text


@admin_only
async def get_codes(message):
    applicants = database.child(firebase_namespace).child("users").get().val()

    codes_message = ""

    for role in message.author.guild.roles:
        if role.name in mission_roles:
            codes_message += "\n\n"
            codes_message += role.name
            codes_message += "\n"
            for member in role.members:
                try:
                    codes_message += applicants[str(member.id)]["mention"]
                    codes_message += "\n"
                    codes_message += applicants[str(member.id)]["pilot_code"]
                    codes_message += "\n"
                    codes_message += applicants[str(member.id)]["mech_token"]
                    codes_message += "\n"
                except KeyError:
                    continue

    await message.channel.send(codes_message)


def is_in_cooldown(applicant_roles):
    return applicant_roles and set(applicant_roles) & set(cooldown_roles)


def is_in_mission(applicant_roles):
    return applicant_roles and (set(applicant_roles) & set(mission_roles))


def get_role_from_name(guild, role_name: str):
    role: Role = discord.utils.get(guild.roles, name=role_name)
    if not role:
        raise ValueError(f"Role {role_name} not found")
    return role


async def remove_roles(member, role_names):
    coroutines = []
    for role_name in role_names:
        role: Role = get_role_from_name(member.guild, role_name)
        coroutines.append(member.remove_roles(role))
    await asyncio.gather(*coroutines)


async def add_role(member, role_name):
    role = get_role_from_name(member.guild, role_name)
    await member.add_roles(role)


def get_applicants():
    if IS_DEV_ENV:
        return {
            f"{QAZZ_ID}": {
                "author_roles": ["@everyone"],
                "id": f"{QAZZ_ID}",
                "mech_token": "#1",
                "mention": f"<@!{QAZZ_ID}>",
                "mission_numbers": ["1"],
                "name": "Test",
                "pilot_code": "1234",
                "weight": 1,
                "timestamp": 1234567890,
            }
        }

    users_table = database.child(firebase_namespace).child("users")
    applicants = users_table.get().val()
    return applicants


async def _move_user_to_cooldown_if_in_mission(guild, applicant_key, applicant):
    applicant_roles = await get_user_roles(guild, applicant_key)
    if is_in_mission(applicant_roles):
        print(applicant["name"], flush=True)
        member = await guild.fetch_member(applicant_key)
        await asyncio.gather(
            remove_roles(member, mission_roles), add_role(member, cooldown_roles[1])
        )


@admin_only
async def move_in_mission_to_on_cooldown(message):
    applicants = get_applicants()

    print("Setting mission members to cooldown week 1", flush=True)
    coroutines = []
    for key, applicant in list(applicants.items()):
        coroutines.append(
            _move_user_to_cooldown_if_in_mission(message.author.guild, key, applicant)
        )
    await asyncio.gather(*coroutines)

    await message.channel.send("New cooldowns set")


@admin_only
async def update_weekly_cooldowns(message):
    applicants = get_applicants()

    print("Updating weekly cooldowns", flush=True)
    for key, applicant in list(applicants.items()):
        applicant_roles = await get_user_roles(message.author.guild, key)
        if applicant_roles:
            if cooldown_roles[2] in applicant_roles:
                member = await message.author.guild.fetch_member(key)
                await remove_roles(member, [cooldown_roles[2]])
            elif cooldown_roles[1] in applicant_roles:
                member = await message.author.guild.fetch_member(key)
                await asyncio.gather(
                    remove_roles(member, [cooldown_roles[1]]),
                    add_role(member, cooldown_roles[2]),
                )
    await message.channel.send("New cooldowns set")


@moderator_only
async def reset_weight(message):
    applicants = database.child(firebase_namespace).child("users").get().val()

    # Remove applications that are older than 30 days
    cutoff = datetime.datetime.now()
    cutoff = cutoff - datetime.timedelta(days=30)
    cutoff_epoch = cutoff.timestamp() * 1000

    for key in list(applicants.keys()):
        if applicants[key]["timestamp"] < cutoff_epoch:
            del applicants[key]

    # Only keep people on cooldown and in missions
    for key in list(applicants.keys()):
        applicant_roles = await get_user_roles(message.author.guild, key)
        if applicant_roles:
            if not (
                (set(applicant_roles) & set(mission_roles))
                or (set(applicant_roles) & set(cooldown_roles))
            ):
                del applicants[key]
        else:
            del applicants[key]

    print("Resetting", flush=True)
    for key in list(applicants.keys()):
        print(applicants[key]["name"], flush=True)
        database.child(firebase_namespace).child("users").child(key).child(
            "weight"
        ).set(0.1)

    await message.channel.send("Weight reset")


@moderator_only
async def hard_reset_weight(message):
    applicants = database.child(firebase_namespace).child("users").get().val()

    print("Resetting", flush=True)
    for key in list(applicants.keys()):
        print(applicants[key]["name"], flush=True)
        database.child(firebase_namespace).child("users").child(key).child(
            "weight"
        ).set(0.1)

    await message.channel.send("Weight hard reset")


@moderator_only
async def increase_weight(message):
    applicants = database.child(firebase_namespace).child("users").get().val()

    # Remove applications that are older than 9 days
    cutoff = datetime.datetime.now()
    cutoff = cutoff - datetime.timedelta(days=9)
    cutoff_epoch = cutoff.timestamp() * 1000

    for key in list(applicants.keys()):
        if applicants[key]["timestamp"] < cutoff_epoch:
            del applicants[key]

    # Remove people on cooldown and in missions
    for key in list(applicants.keys()):
        applicant_roles = await get_user_roles(message.author.guild, key)
        if applicant_roles:
            if (set(applicant_roles) & set(mission_roles)) or (
                set(applicant_roles) & set(cooldown_roles)
            ):
                del applicants[key]
        else:
            del applicants[key]

    print("Increasing", flush=True)
    for key in list(applicants.keys()):
        print(applicants[key]["name"], flush=True)
        database.child(firebase_namespace).child("users").child(key).child(
            "weight"
        ).set(applicants[key]["weight"] * 2)

    await message.channel.send("Weight increased")


async def get_user_roles(guild, user_id):
    try:
        member = await guild.fetch_member(user_id)
        if member:
            return list(map(lambda x: x.name, member.roles))
        else:
            return None
    except Exception as e:
        print(e, flush=True)
        return None


if __name__ == "__main__":
    client.run(os.environ["RALF_JR_DISCORD_TOKEN"])
