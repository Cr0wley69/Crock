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
rooms = {}
ids = []
is_player = {}
guessers = {}
bot = telegram.Bot(config.TOKEN)
admins = {}
words = ["дунаев", "лох", "паша", "тоже", "дамир", "извращенец"]
keywords = {}
is_started = {}


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
    is_player[message.chat_id] = (True, room)
    is_started[room] = False
    bot.send_message(update.message.chat_id, "Айди вашей комнаты: " + room)


def join(update, context):
    msg: telegram.Message = update.message
    room = msg.text.split()[1]
    is_player[msg.chat_id] = (True, room)
    rooms[room].append((msg.chat_id, msg.from_user.username))
    print(rooms)
    print(is_player)
    msg.reply_text("Вы успешно вошли в комнату!")


def leave(update, context):
    message = update.message
    is_player[message.chat_id] = (False, "")
    for room in rooms:
        if (message.chat_id, message.from_user.username) in rooms[room]:
            id = rooms[room].index((message.chat_id, message.from_user.username))
            if admins[room] == (message.chat_id, message.from_user.username):
                for user in rooms[room]:
                    if (message.chat_id, message.from_user.username) == user:
                        continue
                    is_player[user[0]] = (False, "")
                    bot.send_message(user[0], "Комната, в которой вы играли, была закрыта")
                rooms.pop(room)
            else:
                rooms[room].pop(id)
            message.reply_text("Вы успешно вышли из комнаты")
            return
    message.reply_text("Вы еще не вошли в игру")


def answer(update, context):
    msg: telegram.Message = update.message
    if not is_player[msg.chat_id][0]:
        return
    room = is_player[msg.chat_id][1]
    answ = msg.text.split()[1]
    if answ != keywords[room]:
        msg.reply_text("К сожалению, вы не отгадали слово. Попробуйте еще")
    else:
        msg.reply_text("Вы угадали слово, поздравляю! Админ решит, начинать ли новый раунд.")
        players = rooms[room]
        for player in players:
            if player != (msg.chat_id, msg.from_user.username):
                bot.send_message(player[0], "Слово было угадано. Админ решит судьбу этой комнаты")
        is_started[room] = False

def Start(update, context):
    msg: telegram.Message = update.message
    room = is_player[msg.chat_id][1]
    if admins[room] != (msg.chat_id, msg.from_user.username):
        msg.reply_text("Вы не админ, чтобы начинать игру")
        return
    players = rooms[room]
    guesser = random.randint(0, len(players) - 1)
    guessers[room] = players[guesser]
    is_started[room] = True
    for player in players:
        if player == players[guesser]:
            word = random.choice(words)
            keywords[room] = word
            bot.send_message(player[0], "Вы ведущий! Вы должны нарисовать слово {}".format(word))
        else:
            bot.send_message(player[0], "Вы игрок! Вы должны угадать загаданное ведущим слово")
    print(players)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    updater = Updater(config.TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("start_game", Start))
    dp.add_handler(CommandHandler("create", create))
    dp.add_handler(CommandHandler("leave", leave))
    dp.add_handler(CommandHandler("join", join))
    dp.add_handler(CommandHandler("answer", answer))
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
