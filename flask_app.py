from flask import Flask, request, json
import telegram
import os
import random
from quran_search import QuranSearch
from quran_subscriptions_db import QuranSubscriptionsDB

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# set the telegram token here
TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = telegram.Bot(TOKEN)

WORD_BASE_URL = "http://uxquran.com/apps/quran-ayat/"

subscriptionsDb = QuranSubscriptionsDB(os.path.join(app.static_folder, "daily.sqlite"))

HELP_MESSAGE = """Assalamu Alaikum, Welcome to the Noble Quran chatbot.

    To get any ayat and its english translation, send a message in surah:ayat format.
    For eg. send message '2:255' to get ayatul kursi in both english and arabic.

    Commands:
        /random - A random ayat
        /search - Search for arabic/english word in the quran
        /subscribe - Receive a verse daily
        /start - Help on how to use the bot
        /index - List of surahs with indices
        /version - Version of the bot
        /feedback - Send feedback
"""
VERSION = "1.1.1"

@app.route('/{}'.format(TOKEN), methods=['POST'])
def quran_bot_webhook():
    update = telegram.update.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    text = update.message.text.encode('utf-8').decode()
    text = text.lower()
    # the first time you chat with the bot AKA the welcoming message
    if text == "/start":
        bot.sendMessage(chat_id=chat_id, text=HELP_MESSAGE, reply_to_message_id=msg_id)

    elif text == "/index":
        index_message = get_surah_list()
        bot.sendMessage(chat_id=chat_id, text=index_message, reply_to_message_id=msg_id)

    elif text == "/version":
        bot.sendMessage(chat_id=chat_id, text=VERSION, reply_to_message_id=msg_id)

    elif text == "/random":
        indices = get_random_indices()
        surah = indices[0]
        ayat = indices[1]
        surah_name = indices[2]
        surah_display = surah + 1
        ayat_display = ayat + 1
        index_str = "Surah {} ({}:{}) ".format(surah_name, surah_display, ayat_display)
        ar_ayat = "{}\n{}".format(index_str, get_ayat_ar(surah, ayat))
        en_ayat = "{}\n{}".format(index_str, get_ayat_en(surah, ayat))
        bot.sendMessage(chat_id=chat_id, text=ar_ayat)
        bot.sendMessage(chat_id=chat_id, text=en_ayat)
        word_msg = "For word by word meaning:\n" + WORD_BASE_URL + "?sura={}&aya={}".format(surah_display, ayat_display)
        bot.sendMessage(chat_id=chat_id, text=word_msg)

    elif text == "/feedback":
        feedback_msg = "For feedback and suggestions, please send an email to support@uxquran.com"
        bot.sendMessage(chat_id=chat_id, text=feedback_msg, reply_to_message_id=msg_id)

    elif text == "/report":
        feedback_msg = "chat_id={} user_id={}".format(chat_id, update.message.from_user)
        bot.sendMessage(chat_id=chat_id, text=feedback_msg, reply_to_message_id=msg_id)

    elif text == "/subscribe":
        user_name = None
        if update.message.from_user:
            user_name = update.message.from_user["username"]
        if not user_name:
            user_name = update.message.from_user["first_name"]
        if not user_name:
            user_name = chat_id
        subscribe(user_name, chat_id)
        feedback_msg = "You have been successfully subscribed to the daily Quran verses service.\nTo unsubscribe anytime, please send the message /unsubscribe."
        bot.sendMessage(chat_id=chat_id, text=feedback_msg, reply_to_message_id=msg_id)

    elif text == "/unsubscribe":
        unsubscribe(chat_id)
        feedback_msg = "You have been unsubscribed from the daily Quran verses service."
        bot.sendMessage(chat_id=chat_id, text=feedback_msg, reply_to_message_id=msg_id)

    elif "/search" in text:
        # search command
        params = text.split(" ")
        if len(params) > 1:
            input = params[1]
            response_msg = search_word(input)
            bot.sendMessage(chat_id=chat_id, text=response_msg, reply_to_message_id=msg_id)
        else:
            error_msg = "For search, please send message in /search<space><input_word> format.\nFor eg. /search الحمد or /search mercy."
            bot.sendMessage(chat_id=chat_id, text=error_msg, reply_to_message_id=msg_id)
    else:
       try:
            is_arabic = False
            is_english = False
            if ":" in text:
                params = text.split(":")
                if len(params) == 3:
                    # word by word meaning
                    surah = int(params[0]) - 1
                    ayat  = int(params[1]) - 1
                    word  = int(params[2]) - 1

                    if surah > 114 or surah == 114:
                        bot.sendMessage(chat_id=chat_id, text="Sorry, That's an invalid surah number!", reply_to_message_id=msg_id)
                    else:
                        surah_name = get_surah_title(surah)
                        surah_display = surah + 1
                        ayat_display = ayat + 1
                        word_display = word + 1
                        index_str = "Surah {} ({}:{}:{}) ".format(surah_name, surah_display, ayat_display, word_display)
                        en_ayat = "{}\n{}".format(index_str, get_ayat_word(surah, ayat, word))
                        bot.sendMessage(chat_id=chat_id, text=en_ayat)
                        word_msg = "For word by word meaning:\n" + WORD_BASE_URL + "?sura={}&aya={}".format(surah_display, ayat_display)
                        bot.sendMessage(chat_id=chat_id, text=word_msg)
                else:
                    # normal sentences
                    if "ar" in text:
                        is_arabic = True
                        text = text.replace("ar", "")
                        text = text.strip()
                    elif "en" in text:
                        is_english = True
                        text = text.replace("en", "")
                        text = text.strip()

                    params = text.split(":")
                    surah = int(params[0]) - 1
                    ayat  = int(params[1]) - 1

                    if surah > 114 or surah == 114:
                        bot.sendMessage(chat_id=chat_id, text="Sorry, That's an invalid surah number!", reply_to_message_id=msg_id)
                    else:
                        surah_name = get_surah_title(surah)
                        surah_display = surah + 1
                        ayat_display = ayat + 1
                        index_str = "Surah {} ({}:{}) ".format(surah_name, surah_display, ayat_display)

                        ar_ayat = "{}\n{}".format(index_str, get_ayat_ar(surah, ayat))
                        en_ayat = "{}\n{}".format(index_str, get_ayat_en(surah, ayat))
                        # reply_message = "{}\n\n{}".format(quran_ar, quran_en)
                        if is_arabic:
                            bot.sendMessage(chat_id=chat_id, text=ar_ayat)
                        elif is_english:
                            bot.sendMessage(chat_id=chat_id, text=en_ayat)
                        else:
                            bot.sendMessage(chat_id=chat_id, text=ar_ayat)
                            bot.sendMessage(chat_id=chat_id, text=en_ayat)
                            word_msg = "For word by word meaning:\n" + WORD_BASE_URL + "?sura={}&aya={}".format(surah_display, ayat_display)
                            bot.sendMessage(chat_id=chat_id, text=word_msg)
            else:
                bot.sendMessage(chat_id=chat_id, text=HELP_MESSAGE, reply_to_message_id=msg_id)

       except Exception as e:
           # if things went wrong
          #bot.sendMessage(chat_id=chat_id, text=str(e), reply_to_message_id=msg_id)
          error_message = "Sorry, I am not able to understand that. For help send /start."
          bot.sendMessage(chat_id=chat_id, text=error_message, reply_to_message_id=msg_id)

    return 'ok'

def get_ayat_ar(surah, ayat):
    json_data = open(os.path.join(app.static_folder, "quran-ar.json"), "r")
    data = json.load(json_data)
    if surah > 114 or surah == 114:
        return "Invalid surah number. Please send a surah number between 1 and 114."
    if ayat > len(data["quran"]["sura"][surah]["aya"]) or ayat == len(data["quran"]["sura"][surah]["aya"]):
        surahIndex = surah + 1
        return "Invalid ayat number. Surah {} has only {} ayats".format(surahIndex, len(data["quran"]["sura"][surah]["aya"]))
    else:
        return data["quran"]["sura"][surah]["aya"][ayat]["text"]

def get_ayat_en(surah, ayat):
    json_data = open(os.path.join(app.static_folder, "clear.json"), "r")
    data = json.load(json_data)
    if surah > 114 or surah == 114:
        return "Invalid surah number. Please send a surah number between 1 and 114."
    if ayat > len(data["quran"]["sura"][surah]["aya"]) or ayat == len(data["quran"]["sura"][surah]["aya"]):
        surahIndex = surah + 1
        return "Invalid ayat number. Surah {} has only {} ayats".format(surahIndex, len(data["quran"]["sura"][surah]["aya"]))
    else:
        return data["quran"]["sura"][surah]["aya"][ayat]["text"]

def get_ayat_word(surah, ayat, word):
    json_data = open(os.path.join(app.static_folder, "word", "{}.json".format(surah)))
    data = json.load(json_data)
    if surah > 114 or surah == 114:
        return "Invalid surah number. Please send a surah number between 1 and 114."
    if ayat > len(data) or ayat == len(data):
        surahIndex = surah + 1
        return "Invalid ayat number. Surah {} has only {} ayats".format(surahIndex, len(data))
    else:
        return "{}\n{}".format(data[ayat][word]["ar"], data[ayat][word]["tr"])

def get_surah_list():
    json_data = open(os.path.join(app.static_folder, "surahlist.json"), "r")
    data = json.load(json_data)
    index_message = "**Surah List**\n\n"
    for surah in data:
        index_message = index_message + "{}. {}\n".format(surah["number"], surah["transliteration_en"])
    return index_message

def get_random_indices():
    json_data = open(os.path.join(app.static_folder, "surahlist.json"), "r")
    data = json.load(json_data)
    surah = random.randint(0, 113)
    ayat = random.randint(0, data[surah]["total_verses"]-1)
    return surah, ayat, data[surah]["transliteration_en"]

def get_surah_title(surah):
    json_data = open(os.path.join(app.static_folder, "surahlist.json"), "r")
    data = json.load(json_data)
    return data[surah]["transliteration_en"]

def search_word(input):
    data_path = os.path.join(app.static_folder, "wordslist.json")
    results = QuranSearch.search_word(input, count = 5, json_path=data_path)
    response_text = ""
    for item in results:
        response_text = response_text + "\n\n{}:{} ".format(item["word"]["sura"], item["word"]["aya"]) + item["word"]["ar"] + " " + item["word"]["tr"]
    response_text = response_text + "\n\nFor more: " + WORD_BASE_URL + "?search={}".format(input)
    return response_text

def subscribe(user_id, chat_id):
    subscriptionsDb.add_subscription(("{}".format(chat_id), "{}".format(user_id)))

def unsubscribe(chat_id):
    subscriptionsDb.delete_subscription("{}".format(chat_id))



