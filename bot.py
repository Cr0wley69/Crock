import logging

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import config
import random

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
LEN = 10
logger = logging.getLogger(__name__)
message_num = 0
rooms = {}
ids = []
admins = {}


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def generate_id(m):
    s = ""
    for i in range(m):
        c = random.choice([chr(random.randrange(97, 97 + 26)),
                           chr(random.randrange(65, 65 + 26)),
                           str(random.randint(0, 9))])
        while c in ['l', 'I', '0', 'o', 'O', '1']:
            c = random.choice([chr(random.randrange(97, 97 + 26)),
                               chr(random.randrange(65, 65 + 26)),
                               str(random.randint(0, 9))])
        s += c
    return s


def start(update: telegram.Update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi! Используйте команду /help, чтобы узнать мои команды.')


def help(update, context):
    update.message.reply_text(
        'Дунаев лох.')


def create(bot: telegram.Bot, update: telegram.Update, context):
    room = generate_id(LEN)
    while room in ids:
        room = generate_id(LEN)
    ids.append(room)
    admins[room] = (update.message.chat_id, update.message.from_user.username)
    rooms[room] = []
    rooms[room].append((update.message.chat_id, update.message.from_user.username))
    bot.send_message(update.message.chat_id, "Айди вашей комнаты: " + room)


def join(update, context):
    pass


def leave(update, context):
    pass


def answer(update, context):
    pass


def Start(update, context):
    pass


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    updater = Updater(config.TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("help", help))
    bot = telegram.Bot(config.TOKEN)
    dp.add_error_handler(error)
    '''
    if config.HEROKU_APP_NAME is None:
        # Start the Bot


        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        #  SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
    else:
        updater.start_webhook(listen="0.0.0.0",
                              port=config.PORT,
                              url_path=config.TOKEN)
        updater.bot.set_webhook(f"https://{config.HEROKU_APP_NAME}.herokuapp.com/{config.TOKEN}")
        '''
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
