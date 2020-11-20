from discord.ext import commands
from utils import send_message_to_channel
from bot_commands.players import Players
from bot_commands.guilds import Guilds
import os
from dotenv import load_dotenv

load_dotenv()
bot = commands.Bot(command_prefix=os.getenv('BOT_COMMAND_PREFIX'), help_command=None)
bot.add_cog(Guilds())
bot.add_cog(Players())


@bot.event
async def on_command_error(ctx, exception):
    message = 'Empty result'
    exception_type = type(exception)

    if exception_type == commands.errors.CommandNotFound:
        return

    if os.getenv('SEND_DEBUG_TO_CHAT') == 'True' or exception_type == commands.errors.MissingRequiredArgument:
        message = str(exception)

    await send_message_to_channel(ctx, message)


@bot.event
async def on_message(message):
    if not message.content.startswith(os.getenv('BOT_COMMAND_PREFIX')):
        return

    parts = message.content.split(' ', 1)
    parts[0] = parts[0].lower()  # makes bot commands case-insensitive
    message.content = ' '.join(parts)

    await bot.process_commands(message)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


def main():
    print('Connecting...')
    bot.run(os.getenv('DISCORD_TOKEN'))


if __name__ == '__main__':
    main()
