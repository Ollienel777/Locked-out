from random import choice, randint
from discord import Message, Embed
from tasks import master_activity_tasks
import asyncio
import json
import os
import random

DATA_FILE = "user_data.json"

BADGE_REQUIREMENTS = {
    "<:bronzebadge:1365803704065724416> Bronze": 100,
    "<:silverbadge:1365803717839945751> Silver": 300,
    "<:goldbadge:1365803731635142696> Gold": 1000
}

# Strand mastery badges
STRAND_BADGE_REQUIREMENTS = {
    "Creativity": ("<:creativityicon1:1365762192145776811> Creativity Master", 100),
    "Skill-building": ("<:skillsicon1:1365762155609329734> Skill-building Master", 100),
    "Physical/Well-being": ("<:healthicon1:1365762172617101323> Physical Master", 100),
    "Leisure": ("<:leisureicon1:1365762207656185956> Leisure Master", 100),
    "Learning": ("<:readingicon1:1365762141042380800> Learning Master", 100),
    "Social": ("<:socialicon1:1365762120712589382> Social Master", 100)
}

activities = {
            "Creativity": [
                "Painting", "Pastel", "DigitalArt", "Sketching", "GraphicDesign", "Baking", "Cooking", "Photography", "Videography", "Collage", "TextileArts", "Accessories", "Origami", "Journaling", "Singing", "Rapping", "Poetry", "Gardening", "Calligraphy", "Beatboxing", "Penbeat", "Songwriting", "CreativeWriting", "Drama"
            ],
            "Skill-building": [
                "Juggling","RubixCubing","MagicTricks","CardManipulation","Coding","Chess"
            ],
            "Physical/Well-being":[
                "Cardio","Dance","HIIT","Yoga","Frisbee"
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
# Reverse map: activity_name -> strand_name
activity_to_strand = {}
for strand, acts in activities.items():
    for act in acts:
        activity_to_strand[act] = strand


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
            "activities": {},
            "badges": {},
            "activity_tracks": {}
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

    badges = list(user_data.get("badges", {}).keys())

    if badges:
        badge_text = " ".join(badges)
    else:
        badge_text = "No badges yet."

    embed.add_field(name="**Badges**", value=badge_text, inline=False)
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

    if selected_activity not in user_profile["activity_tracks"]:
        user_profile["activity_tracks"][selected_activity] = {
        "exp": 25,
        "tasks_completed": 0,
        "current_tasks": [
            master_activity_tasks[selected_activity][0]["name"],
            master_activity_tasks[selected_activity][1]["name"],
            master_activity_tasks[selected_activity][2]["name"]
        ]
    }
    save_user_data(data)

async def show_unlocked_activities(client, message: Message, username: str, user_data: dict) -> None:
    unlocked = user_data.get("unlocked_activities", [])

    if not unlocked:
        await message.channel.send(f"{username}, you haven't unlocked any activities yet! Keep going! 🚀")
        return

    formatted_activities = "\n- " + "\n- ".join(unlocked)
    await message.channel.send(
        f"**{username}'s Unlocked Activities:**\n{formatted_activities}"
    )

async def show_activity_track(client, message: Message, username: str, user_data: dict, activity_name: str) -> None:
    activity_data = user_data.get("activity_tracks", {}).get(activity_name, None)

    if not activity_data:
        await message.channel.send(f"{username}, you haven't unlocked {activity_name} yet!")
        return

    embed = Embed(
        title=f"{username}'s {activity_name} Journey",
        description=f"**Total {activity_name} EXP:** {activity_data['exp']}",
        color=0x00FFAA
    )

    for idx, task_name in enumerate(activity_data["current_tasks"], start=1):
        # Find the EXP associated with the task
        master_tasks = master_activity_tasks.get(activity_name, [])
        task_info = next((task for task in master_tasks if task["name"] == task_name), None)

        if task_info:
            exp_amount = task_info["exp"]
            value = f"{task_name} ({exp_amount} EXP)"
        else:
            value = f"{task_name}"

        embed.add_field(name=f"Task {idx}", value=value, inline=False)
    await message.channel.send(embed=embed)

async def complete_activity_task(client, message: Message, username: str, user_data: dict, activity_name: str, task_num: int) -> None:
    activity_data = user_data.get("activity_tracks", {}).get(activity_name, None)

    if not activity_data:
        await message.channel.send(f"{username}, you haven't unlocked {activity_name} yet! 🔒")
        return

    current_tasks = activity_data.get("current_tasks", [])

    if not (1 <= task_num <= len(current_tasks)):
        await message.channel.send(f"{username}, invalid task number! Pick 1, 2, or 3. ❌")
        return

    selected_task_name = current_tasks[task_num - 1]

    # Find EXP value for the selected task
    master_tasks = master_activity_tasks.get(activity_name, [])
    task_info = next((task for task in master_tasks if task["name"] == selected_task_name), None)

    if not task_info:
        await message.channel.send(f"Error: Could not find task info for {selected_task_name}! ⚠️")
        return

    exp_reward = task_info["exp"]

    # Award EXP
    activity_data["exp"] += exp_reward
    activity_data["tasks_completed"] += 1

    # Replace completed task with the next one
    next_index = activity_data["tasks_completed"] + 2  # +2 because user always sees 3 tasks
    if next_index < len(master_tasks):
        next_task = master_tasks[next_index]["name"]
        activity_data["current_tasks"][task_num - 1] = next_task
    else:
        # No more tasks, mark as completed
        activity_data["current_tasks"][task_num - 1] = "🎉 Completed 🎉"

    # Update total EXP
    user_data["total_exp"] += exp_reward

    # Update strand EXP
    strand = activity_to_strand.get(activity_name, None)
    if strand:
        if strand not in user_data["strands"]:
            user_data["strands"][strand] = 0  # Initialize if missing
        user_data["strands"][strand] += exp_reward

        # Save changes
        all_data = load_user_data()
        all_data[username] = user_data
        save_user_data(all_data)
    
    for badge, required_exp in BADGE_REQUIREMENTS.items():
        if user_data["total_exp"] >= required_exp and badge not in user_data["badges"]:
            user_data["badges"][badge] = True  # Mark as earned
    
    strand = activity_to_strand.get(activity_name, None)
    if strand:
        if strand not in user_data["strands"]:
            user_data["strands"][strand] = 0
        user_data["strands"][strand] += exp_reward

        # Now check if user qualifies for a strand badge
        strand_badge, strand_required_exp = STRAND_BADGE_REQUIREMENTS.get(strand, (None, None))
        if strand_badge and user_data["strands"][strand] >= strand_required_exp and strand_badge not in user_data["badges"]:
            user_data["badges"][strand_badge] = True
    
    save_user_data(all_data)

    await message.channel.send(
        f"✅ {username} completed **{selected_task_name}** and earned **{exp_reward} EXP** in **{activity_name}**! 🚀"
    )

async def help_command(message: Message):
    help_message = """
    **GENOVA Help Guide**

    **$profile** - Creates a new profile or displays your current progress in GENOVA, including your total EXP, EXP in each category, and badges you've earned.
    
    **$activity** - Generates two random activities from the category you choose. Reply with a category number (1-6) for the activity you want to try.
    
    **$[activity]** - Displays the total EXP you’ve earned in this specific activity and shows the next tasks you need to complete to progress.
    
    **$[activity 1]** - Completes the first task in the list for the specific activity. You’ll earn EXP for this task and move closer to leveling up in that activity.
    
    **Example usage**:
    `$profile`: To check your profile.
    `$activity`: To get random activity suggestions.
    `$Cooking`: To see your progress in the Cooking activity.
    `$Cooking 1`: To complete the first task in the Cooking activity.

    **Note**: Type `$help` for this help message anytime!

    """

    await message.channel.send(help_message)
    
def user_profile_prompt(user_input: str, username: str = "", pfp_url: str = "") -> str:
    lowered: str = user_input.lower()    
    if lowered.startswith('profile'):
        create_user_profile(username)
        return get_profile_card(username, pfp_url)
