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
is_player = {}
bot = telegram.Bot(config.TOKEN)
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


def create(update: telegram.Update, context):
    message = update.message
    if (message.chat_id in is_player) and is_player[message.chat_id]:
        message.reply_text("Вы не можете создать новую комнату, находясь уже в комнате")
        return
    room = generate_id(LEN)
    while room in ids:
        room = generate_id(LEN)
    ids.append(room)
    admins[room] = (message.chat_id, message.from_user.username)
    rooms[room] = []
    rooms[room].append((message.chat_id, message.from_user.username))
    is_player[message.chat_id] = True
    bot.send_message(update.message.chat_id, "Айди вашей комнаты: " + room)


def join(update, context):
    msg: telegram.Message = update.message
    room = msg.text.split()[1]
    is_player[msg.chat_id] = True
    rooms[room].append((msg.chat_id, msg.from_user.username))
    msg.reply_text("Вы успешно вошли в комнату!")


def leave(update, context):
    message = update.message
    is_player[message.chat_id] = False
    for room in rooms:
        if (message.chat_id, message.from_user.username) in rooms[room]:
            id = rooms[room].index((message.chat_id, message.from_user.username))
            if admins[room] == (message.chat_id, message.from_user.username):
                for user in rooms[room]:
                    if (message.chat_id, message.from_user.username) == user:
                        continue
                    is_player[user[0]] = False
                    bot.send_message(user[0], "Комната, в которой вы играли, была закрыта")
                rooms.pop(room)
            else:
                rooms[room].pop(id)
            message.reply_text("Вы успешно вышли из комнаты")
            return
    message.reply_text("Вы еще не вошли в игру")


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
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("create", create))
    dp.add_handler(CommandHandler("leave", leave))
    dp.add_handler(CommandHandler("join", join))
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
