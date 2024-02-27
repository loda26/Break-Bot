from typing import Final
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime

TOKEN: Final = 'API token of the bot'
BOT_USERNAME: Final = 'Name of the bot' # here was the name of my bot was @test_newbreak_bot

MAX_BREAK_COUNT: Final = 3      # Maximum number of people allowed to take a break simultaneously
break_set = {}
user_last_break = {}
EXEMPT_USER_ID: Final = 1800042272

# commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Welcome to the break bot? use /gotobreak to start your break.')

# Modify your gotobreak_command
async def gotobreak_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Check if the user is exempt
    if user_id == EXEMPT_USER_ID:
        break_set[user_id] = datetime.now()
        await update.message.reply_text('Go and enjoy your break, use /backfrombreak when you come back.')
    else:
        # Check if the user is not already on a break and within the maximum count
        if user_id not in break_set:
            if len(break_set) < MAX_BREAK_COUNT:
                break_set[user_id] = datetime.now()
                await update.message.reply_text('Go and enjoy your break, use /backfrombreak when you come back.')
            else:
                await update.message.reply_text('Sorry, No slots avaliable now, wait till someone come back')
        else:
            await update.message.reply_text('you are already on a break, use /backfrombreak')


async def backfrombreak_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in break_set:
        break_start_time = break_set.pop(user_id)
        break_duration = datetime.now() - break_start_time

        if user_id in user_last_break:
            total_break_duration = user_last_break[user_id] + break_duration
        else:
            total_break_duration = break_duration

        user_last_break[user_id] = total_break_duration

        break_duration_str = str(break_duration).split(".")[0]
        total_break_duration_str = str(total_break_duration).split(".")[0]

        await update.message.reply_text(
            f'Welcome back 5o4 hat leads, You spent {break_duration_str} on this break.'
            f'\nTotal break time: {total_break_duration_str}.'
        )
    else:
        await update.message.reply_text('You are not currently on a break.')

async def outage_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id == EXEMPT_USER_ID:
        break_set[user_id] = user_id
        await update.message.reply_text('use /backfromoutage when you come back')
    else:
        if user_id not in break_set:
            break_set[user_id] = user_id
            await update.message.reply_text('use /backfromoutage when you come back')
        else:
            await update.message.reply_text('You are already resting, use /backfromoutage')

async def backfromoutage_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in break_set:
        break_set.pop(user_id)
        await update.message.reply_text('Welcome back')
    else:
        await update.message.reply_text('You are not currently on a break.')

async def whoinbreak_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not break_set:
        await update.message.reply_text('No one is currently on a break.')
    else:
        user_names = await get_user_names(context, break_set.keys())
        await update.message.reply_text(f'Users currently on a break: {", ".join(user_names)}')


async def get_user_names(context, user_ids: set) -> list:
    user_names = []
    for user_id in user_ids:
        try:
            user = await context.bot.get_chat(user_id)
            user_names.append(user.username or f"User {user_id}")
        except Exception as e:
            print(f"Error getting user {user_id}: {str(e)}")

    return user_names

if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('gotobreak', gotobreak_command))
    app.add_handler(CommandHandler('backfrombreak', backfrombreak_command))
    app.add_handler(CommandHandler('outage', outage_command))
    app.add_handler(CommandHandler('backfromoutage', backfromoutage_command))
    app.add_handler(CommandHandler('whoinbreak', whoinbreak_command))

    print('Polling...')

    app.run_polling(poll_interval=3)
