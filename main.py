from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import get_response

#Load our token from somewhere safe.
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
print(TOKEN)

#Bot setup
intents: Intents = Intents.default()
intents.message_content = True # NOQA
client: Client = Client(intents=intents)

#Sending Messages + sending in private
async def send_message(message: Message, user_message: str, username: str) -> None:
    if not user_message:
        print("(message was empty because intents were not enabled)")
        return

    try:
        response: str = get_response(user_message, username)
        await message.channel.send(response)
    except Exception as e:
        print(e)


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

    print(f'[{channel}] {username}: "{user_message}"')
    content = user_message.strip()

    if not content.startswith('$'):
        return

    command = content[1:]  # remove $

    await send_message(message, command, username)

#Step 5: Main entry point
def main() -> None:
    client.run(token=TOKEN)

if __name__ == '__main__':
    main()


