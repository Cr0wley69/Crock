import logging
import sqlite3
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import config
import random

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
LEN = 10  # длина id комнаты
logger = logging.getLogger(__name__)
rooms = {}  # список комнат
ids = []  # список айдишников комнат
is_player = {}  # список игроков
guessers = {}  # список ведущих
bot = telegram.Bot(config.TOKEN)
admins = {}  # список админов
words = ["дунаев", "лох", "паша", "тоже", "дамир", "извращенец"]  # слова
keywords = {}  # загаданные слова
is_started = {}  # начатые игры


# генератор id комнаты
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


# команда /start
def start(update: telegram.Update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi! Используйте команду /help, чтобы узнать мои команды.')


# команда /help
def help(update, context):
    update.message.reply_text(
        'Дунаев лох.\n\
        /reg - зарегистрироваться в боте\n\
        /create - создать комнату, где будет проходить игра, бот присылает id вашей комнаты\n\
        /leave - выйти из комнаты\n\
        /join <id комнаты> - зайти в игру с этой комнатой\n\
        /start_game - начать игру (команда для создателя комнаты)\n\
        /answer <слово> - дать вариант ответа\n\
        /stats - статистика по игроку\n\
        ')


# команда /create
def create(update: telegram.Update, context):
    message = update.message
    con = sqlite3.connect("crocodile.db")
    cur = con.cursor()
    query = "SELECT * FROM users WHERE id == " + str(message.chat_id)
    result = cur.execute(query).fetchall()
    if not len(result):
        message.reply_text("Вы не зарегистрированы.")
        return
    if (message.chat_id in is_player) and is_player[message.chat_id][0]:
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


# команда /reg
def reg(update, context):
    msg = update.message
    con = sqlite3.connect("crocodile.db")
    cur = con.cursor()
    query = "SELECT * FROM users WHERE id == {}".format(msg.chat_id)
    result = cur.execute(query).fetchall()
    if len(result):
        msg.reply_text("Вы уже зарегистрированы")
        return
    query = "INSERT INTO users VALUES ({}, '{}', 1, 0)".format(msg.chat_id, msg.from_user.username)
    result = cur.execute(query).fetchall()
    con.commit()
    msg.reply_text("Вы успешно зарегистрировались!")


# команда /join
def join(update, context):
    msg: telegram.Message = update.message
    try:
        con = sqlite3.connect("crocodile.db")
        cur = con.cursor()
        query = "SELECT * FROM users WHERE id == " + str(msg.chat_id)
        result = cur.execute(query).fetchall()
        if not len(result):
            msg.reply_text("Вы не зарегистрированы.")
            return
        if (msg.chat_id in is_player) and is_player[msg.chat_id][0]:
            msg.reply_text("Вы не можете войти в другую комнату, находясь уже в комнате")
            return
        room = msg.text.split()[1]
        is_player[msg.chat_id] = (True, room)
        rooms[room].append((msg.chat_id, msg.from_user.username))
        msg.reply_text("Вы успешно вошли в комнату!")
    except Exception:
        msg.reply_text("Произошла ошибка. Скорее всего вы неверно ввели номер комнаты")


# команда /leave
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


# команда /answer
def answer(update, context):
    msg: telegram.Message = update.message
    con = sqlite3.connect("crocodile.db")
    cur = con.cursor()
    if (msg.chat_id not in is_player) or (is_player[msg.chat_id][0] == False):
        msg.reply_text("Вы еще не вошли в игру")
        return
    room = is_player[msg.chat_id][1]
    if guessers[room][0] == msg.chat_id:
        msg.reply_text("Вы ведущий, так что не можете отгадывать слова")
        return
    try:
        answ = msg.text.split()[1]
        if answ != keywords[room]:
            msg.reply_text("К сожалению, вы не отгадали слово. Попробуйте еще")
        else:
            query = "SELECT wins FROM users WHERE id == {}".format(msg.chat_id)
            result = cur.execute(query).fetchall()
            query = "UPDATE users SET wins = {} WHERE id == {}".format(result[0][0] + 1, msg.chat_id)
            result = cur.execute(query)
            con.commit()
            msg.reply_text("Вы угадали слово, поздравляю! Админ решит, начинать ли новый раунд.")
            players = rooms[room]
            for player in players:
                if player != (msg.chat_id, msg.from_user.username):
                    bot.send_message(player[0], "Слово было угадано. Админ решит судьбу этой комнаты")
            is_started[room] = False
    except Exception:
        msg.reply_text("Произошла ошибка. Скорее всего вы не ответ.")


# команда /start_game
def Start(update, context):
    msg: telegram.Message = update.message
    con = sqlite3.connect("crocodile.db")
    cur = con.cursor()
    if (msg.chat_id not in is_player) or (is_player[msg.chat_id][0] == False):
        msg.reply_text("Вы еще не вошли в игру")
        return
    room = is_player[msg.chat_id][1]
    if admins[room] != (msg.chat_id, msg.from_user.username):
        msg.reply_text("Вы не админ, чтобы начинать игру")
        return
    players = rooms[room]
    guesser = random.randint(0, len(players) - 1)
    guessers[room] = players[guesser]
    is_started[room] = True
    for player in players:
        query = "SELECT games FROM users WHERE id == {}".format(player[0])
        result = cur.execute(query).fetchall()
        query = "UPDATE users SET games = {} WHERE id == {}".format(result[0][0] + 1, player[0])
        result = cur.execute(query)
        con.commit()
        if player == players[guesser]:
            word = random.choice(words)
            keywords[room] = word
            bot.send_message(player[0], "Вы ведущий! Вы должны нарисовать слово {}".format(word))
        else:
            bot.send_message(player[0], "Вы игрок! Вы должны угадать загаданное ведущим слово")
    print(players)


# команда /stats
def stats(update, context):
    msg: telegram.Message = update.message
    con = sqlite3.connect("crocodile.db")
    cur = con.cursor()
    query = "SELECT * FROM users WHERE id == {}".format(msg.chat_id)
    result = cur.execute(query).fetchall()[0]
    if len(result) == 0:
        msg.reply_text("Вы не зарегистрированы")
        return
    message = "Статистика игрока " + result[1] + '\n'
    message += "Количество игр: " + str(result[2]) + '\n'
    message += "Количество побед: " + str(result[3])
    msg.reply_text(message)


# вывод ошибок в консоль
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    updater = Updater(config.TOKEN, use_context=True)
    dp = updater.dispatcher
    # подключаем команды
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("start_game", Start))
    dp.add_handler(CommandHandler("create", create))
    dp.add_handler(CommandHandler("reg", reg))
    dp.add_handler(CommandHandler("leave", leave))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("join", join))
    dp.add_handler(CommandHandler("answer", answer))
    dp.add_error_handler(error)
    # запускаем бота
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
