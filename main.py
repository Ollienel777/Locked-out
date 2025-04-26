from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, Embed
from responses import gen_new_activity, show_unlocked_activities, show_activity_track, complete_activity_task, create_user_profile, get_profile_card

DATA_FILE = "user_data.json"


#Load our token from somewhere safe.
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
print(TOKEN)

#Bot setup
intents: Intents = Intents.default()
intents.message_content = True # NOQA
client: Client = Client(intents=intents)

#Sending Messages + sending in private


#Handling the startup for our bot
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')

#Handling incoming messages
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)
    pfp_url = message.author.avatar.url if message.author.avatar else message.author.default_avatar.url


    print(f'[{channel}] {username}: "{user_message}"')
    content = user_message.strip()

    if not content.startswith('$'):
        return

    command = content[1:]  # remove $
    parts = command.split()
    activity_name = parts[0].capitalize()  # 'baking' -> 'Baking'
    task_choice = int(parts[1]) if len(parts) > 1 else None

    if command.startswith('profile'):
        create_user_profile(username)
        profile_embed = get_profile_card(username, pfp_url)
        await message.channel.send(embed=profile_embed)
        return

    if command.startswith('activity'):
        await gen_new_activity(client, message, username)
        return

    from responses import load_user_data  # You can import it once at top of file globally later

    data = load_user_data()

    if username not in data:
        await message.channel.send(f"{username}, you don't have a profile yet. Use `$profile` to create one!")
        return

    user_data = data[username]

    if command.startswith('unlocked'):
        await show_unlocked_activities(client, message, username, user_data)
        return

    # Handle activity showing or task completion
    if task_choice is None:
        await show_activity_track(client, message, username, user_data, activity_name)
        return
    else:
        await complete_activity_task(client, message, username, user_data, activity_name, task_choice)
        return


#Step 5: Main entry point
def main() -> None:
    client.run(token=TOKEN)

if __name__ == '__main__':
    main()


