from random import choice, randint
from discord import Message, Embed
import asyncio
import json
import os
import random

DATA_FILE = "user_data.json"

activities = {
            "Creativity": [
                "Acrylic Painting", "Oil pastel", "Digital art", "Sketching", "Graphic design", "Baking", "Cooking", "Photography/Photo editing", "Videography/Video editing", "Collage", "Knitting/Crochet/Embroidery", "Make accessories", "Origami", "Journaling", "Singing", "Rapping", "Poetry writing", "Gardening", "Calligraphy", "Beatboxing", "Penbeat", "Songwriting/Composing", "Creative writing", "Drama/Acting/Monologues (recreate a scene from your favourite show!)"
            ],
            "Skill-building": [
                "Juggling","Rubix Cubing","Magic Tricks","Card Manipulation","Coding","Chess"
            ],
            "Physical/Well-being":[
                "Cardio (Jump roping, running)","Dance","HIIT Workouts","Stretching/Yoga","Frisbee"
            ],
            "Leisure":[
                "Play a new boardgame","Start a new show/movie","Find new artists/listen to new songs"
            ],
            "Learning":[
                "New language", "Wikepedia Page Marathon","Learn Morse Code", "Learn a sentence in Sign Language", "Start a new book"
            ],
            "Social": [
                "Join a new server of interest", "Participate in a micrograme with a group of friends (e.g. pictionary)", "Host a small call with friends and check in with them", "Challenge friends to trivia", "Play co-op games", "Make a collaborative playlist", "Have an award ceremony with friends (e.g. most likely to...)"
            ]
        }
ALL_STRANDS = {
    "1": "Creativity",
    "2": "Skill-building",
    "3": "Physical/Well-being",
    "4": "Leisure",
    "5": "Reading/Learning",
    "6": "Social"
}
def load_user_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({}, f)

    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_user_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def create_user_profile(username: str) -> str:
    data = load_user_data()
    if username not in data:
        # Create a new profile structure
        data[username] = {
            "total_exp": 0,
            "strands": {},
            "activities": {}
        }

        # Initialize strands
        for strand in activities.keys():
            data[username]["strands"][strand] = 0

        # Initialize individual activities
        for strand, acts in activities.items():
            for act in acts:
                data[username]["activities"][act] = 0

        save_user_data(data)
        return f"{username}, your profile has been created! Let's start earning EXP! 🎯"
        

def get_profile_card(username: str, pfp_url: str) -> Embed:
    data = load_user_data()

    if username not in data:
        embed = Embed(title="Error", description=f"{username}, you don't have a profile yet. Use `$profile` to create one!", color=0xFF0000)
        return embed

    user_data = data[username]
    total_exp = user_data.get("total_exp", 0)
    strands = user_data.get("strands", {})

    # Create an Embed
    embed = Embed(
        title=f"{username}'s Profile",
        description=f"**Total EXP:** {total_exp}",
        color=0x00ffcc  # Light blue/green color
    )

    # Add a small profile picture thumbnail
    embed.set_thumbnail(url=pfp_url)

    # Add each strand and its EXP as fields
    for strand, exp in strands.items():
        embed.add_field(name=strand, value=f"{exp} EXP", inline=True)

    return embed


async def gen_new_activity(client, message: Message, username: str) -> None:
    strand_list = (
        "Choose a strand from the following options:\n"
        "1. Creativity\n"
        "2. Skill-building\n"
        "3. Physical/Well-being\n"
        "4. Leisure\n"
        "5. Reading/Learning\n"
        "6. Social\n\n"
        "Reply with a number (1-6) to pick your preferred category!"
    )
    await message.channel.send(strand_list)

    def check(m: Message) -> bool:
        return m.author == message.author and m.channel == message.channel

    try:
        reply = await client.wait_for('message', check=check, timeout=30.0)
    except asyncio.TimeoutError:
        await message.channel.send(f"{username}, you took too long to respond. Please try again later.")
        return

    activity_input = reply.content.strip()
    strand = ALL_STRANDS.get(activity_input)

    if not strand:
        await message.channel.send("Invalid choice. Please type a number between 1 and 6 next time!")
        return

    if strand not in activities or not activities[strand]:
        await message.channel.send(f"Sorry, there are no activities available for **{strand}** right now.")
        return

    activity_choices = random.sample(activities[strand], k=min(2, len(activities[strand])))

    activity_message = (
        f"Here are two activities you could try from **{strand}**:\n"
        f"1. {activity_choices[0]}\n"
        f"2. {activity_choices[1]}\n\n"
        "Reply with **1** or **2** to pick the activity you want to do!"
    )
    await message.channel.send(activity_message)

    try:
        choice_reply = await client.wait_for('message', check=check, timeout=30.0)
    except asyncio.TimeoutError:
        await message.channel.send(f"{username}, you took too long to choose an activity. Please try again later.")
        return

    choice = choice_reply.content.strip()

    if choice == "1":
        selected_activity = activity_choices[0]
    elif choice == "2":
        selected_activity = activity_choices[1]
    else:
        await message.channel.send("Invalid selection. Please type **1** or **2** next time!")
        return

    await message.channel.send(f"Awesome! You chose **{selected_activity}**. Have fun, {username}! 🎉")

    # 🛠 NEW: Save to user_data.json
    data = load_user_data()

    if username not in data:
        await message.channel.send(f"Error: {username} does not have a profile yet. Please use `$profile` first!")
        return

    user_profile = data[username]

    # Initialize unlocked_activities list if not exists
    if "unlocked_activities" not in user_profile:
        user_profile["unlocked_activities"] = []

    if selected_activity not in user_profile["unlocked_activities"]:
        user_profile["unlocked_activities"].append(selected_activity)

    # Add 25 EXP to the activity
    if selected_activity not in user_profile["activities"]:
        user_profile["activities"][selected_activity] = 0
    user_profile["activities"][selected_activity] += 25

    # Update total EXP
    user_profile["total_exp"] += 25

    # Update corresponding strand EXP
    if strand not in user_profile["strands"]:
        user_profile["strands"][strand] = 0
    user_profile["strands"][strand] += 25

    # Save the changes
    save_user_data(data)

    await message.channel.send(f"✅ You've unlocked **{selected_activity}** and gained **25 EXP** towards **{strand}**!")

def get_response(user_input: str, username: str = "", pfp_url: str = "") -> str:
    lowered: str = user_input.lower()

    if lowered.startswith('log') or lowered.startswith('l'):
        return 'hello :)'
    
    if lowered.startswith('profile'):
        create_user_profile(username)
        return get_profile_card(username, pfp_url)
