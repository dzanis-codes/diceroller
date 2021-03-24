## TODO
## 1. akciju saraksts ar chatid
## 2. publiskais čats redz tikai info ka jaiet balsot individuali un rezultatus
## 3. rezultatos redz sarakstu, kas nav nobalsojusi
## 4. /manasbalsis funkcionalitate redzet savu skaitu pret kopejo
## 5. /mainitnalsi funkcionalitate
## 6. /jaunsbalsojums funckionalitate


import logging
import time
import sqlite3


from telegram import (
    Poll,
    ParseMode,
    KeyboardButton,
    KeyboardButtonPollType,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    PollAnswerHandler,
    PollHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

reply_keyboard = [
    ['1. opcija PAR', '2.opcija PRET'],
    ['3. Taureņa opcija kautkas alternatīvs', '4. atturos/par maz info'],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

keyboard_text = ['1. opcija PAR', '2.opcija PRET',
    '3. Taureņa opcija kautkas alternatīvs', '4. atturos/par maz info']

conn = sqlite3.connect('skaititajs.db')
c = conn.cursor()


table_title = "results-" + time.strftime("%y", time.gmtime()) + "-" + time.strftime("%w", time.gmtime())
c.execute('''CREATE TABLE IF NOT EXISTS balsis
           (id INTEGER PRIMARY KEY, balsojuma_id, jautajums, balsotajs, balsu_skaits, balsojuma_opcija, timestamp)''')
conn.commit()

##commit 1.ierakstu
balsojuma_id = 1
jautajums = "Jautājums balsošanai (Nr.x): Vai atbalstāt investīciju piedāvājumu, kā aprakstīja dobis kur kaut ko iegādās un kaut kas notiks?"
balsotajs = 0
balsu_skaits = 0
balsojuma_opcija = 0
timestamp = 0
sql_entry = (balsojuma_id, str(jautajums), balsotajs, balsu_skaits, balsojuma_opcija, timestamp)
c.execute("INSERT INTO balsis VALUES (null, ?, ?, ?, ?, ?, ?)", sql_entry)
conn.commit()


##shis pilnais nepbuliski

balsis = 90
balsu_saraksts = {'xx': 1300, 'yy': 13500, 'zz': 3500}
chat_saraksts = {'dzanis': '2042772'}

def lastSession():
    conn = sqlite3.connect('skaititajs.db')
    c = conn.cursor()
    c.execute("SELECT max(balsojuma_id) FROM balsis" )
    last_session_id=c.fetchone()
    return last_session_id

def countvotes():
    #sheit vajadzes funkciju, lai saskaita visus četrus ablsojumus un izdod četrus rezultātus ārā
    balsojuma_nr = lastSession()
    conn = sqlite3.connect('skaititajs.db')
    c = conn.cursor()
    votes = []
    for opcija in range(4):
        c.execute("SELECT sum(balsu_skaits) FROM balsis WHERE balsojuma_id = ? AND balsojuma_opcija = ?", (balsojuma_nr, opcija) )
        votes.append(c.fetchone()[0])
    print(votes)
    return votes

def start(update: Update, _: CallbackContext) -> None:
    """Inform user about what this bot can do"""
    if update.message.chat['type'] == 'private':
        update.message.reply_text(
        'Izvēlēties /balsot lai balsotu un /rezultati lai apskatītu rezultātus, bet tas otrais variants vel nav pabeigts.'
        )
    else:
        update.message.reply_text(
        'Pašu balsošanu vajag veikt ar robotu individuālā čatā, uzspied viņam, ieej un uzraksti /start, šeit var tikai apskatīties /rezultati'
        )

def echo(update: Update, _: CallbackContext) -> None:
    """Echo the user message."""
    one = ReplyKeyboardRemove(remove_keyboard = True)
    print(update.message.chat['id'])
    print(update.message.chat['type'])
    print(update.message.chat)
    ##ja balsojums neeksistē, tad pievieno ierakstu, bet ja eksistē, tad ir nobalsots, bet ja nav vispār tāda, tad ta ari pasaka

    for index in range(len(keyboard_text)):

        if update.message.text == keyboard_text[index]:
            chat_id = update.message.chat['id']
            print(balsu_saraksts[str(chat_id)])

            votingSession=(lastSession()[0])
            conn = sqlite3.connect('skaititajs.db')
            c = conn.cursor()
            c.execute("""SELECT balsojuma_id, balsotajs FROM balsis WHERE balsojuma_id=?
            AND balsotajs=?""", (votingSession, chat_id))
            unique_check = c.fetchone()
            if unique_check:
                text = "vienreiz jau nobalsots"
                update.message.reply_text(text, reply_markup=one)
            else:
                text = "ok nobalsots"
                update.message.reply_text(text, reply_markup=one)
                balsojuma_id = votingSession
                jautajums = "Jautājums balsošanai (Nr.x): Vai atbalstāt investīciju piedāvājumu, kā aprakstīja dobis kur kaut ko iegādās un kaut kas notiks?"
                balsotajs = chat_id
                balsu_skaits = balsu_saraksts[str(chat_id)]
                balsojuma_opcija = index
                timestamp = 0
                sql_entry = (balsojuma_id, str(jautajums), balsotajs, balsu_skaits, balsojuma_opcija, timestamp)
                c.execute("INSERT INTO balsis VALUES (null, ?, ?, ?, ?, ?, ?)", sql_entry)
                conn.commit()


    update.message.reply_text(update.message.text, reply_markup=one)


def poll(update: Update, context: CallbackContext) -> None:
    """Sends a predefined poll"""

    reply_text = "Jautājums balsošanai (Nr.x): Vai atbalstāt investīciju piedāvājumu, kā aprakstīja dobis kur kaut ko iegādās un kaut kas notiks?"
    update.message.reply_text(reply_text, reply_markup=markup)

def rezultati(update: Update, context: CallbackContext) -> None:
    one = ReplyKeyboardRemove(remove_keyboard = True)
    print(update.message.chat['id'])
    print(update.message.chat['type'])

    votes = countvotes()
    
    votes1 = str(round(100 * int(votes[0]) / balsis, 2))+"%"
    votes2 = str(round(100 * int(votes[1]) / balsis, 2))+"%"
    votes3 = str(round(100 * int(votes[2]) / balsis, 2))+"%"
    votes4 = str(round(100 * int(votes[3]) / balsis, 2))+"%"
    text = "Par pirmo opciju nobalsojuši " + votes1 + ", par otro " + votes2 + ", par trešo " + votes3 + ", par ceturto " + votes4
    update.message.reply_text(text, reply_markup=one)
    

def jauns_balsojums(update: Update, context: CallbackContext) -> None:

    print(update.message.chat['id'])
    print(update.message.chat['type'])
    #ja tas esmu es, tad jaieliek jauns id, viens jauns ieraksts ar 0 balsīm un balsojuma temats jauns




def help_handler(update: Update, _: CallbackContext) -> None:
    """Display a help message"""
    if update.message.chat['type'] == 'private':
        update.message.reply_text(
        'Izvēlēties /balsot lai balsotu un /rezultati lai apskatītu rezultātus, bet tas otrais variants vel nav pabeigts.'
        )
    else:
        update.message.reply_text(
        'Pašu balsošanu vajag veikt ar robotu individuālā čatā, uzspied viņam, ieej un uzraksti /start, šeit var tikai apskatīties /rezultati'
        )

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater("token")
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('balsot', poll))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    dispatcher.add_handler(CommandHandler('help', help_handler))
    dispatcher.add_handler(CommandHandler('jauns', jauns_balsojums))
    dispatcher.add_handler(CommandHandler('rezultati', rezultati))





    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()



