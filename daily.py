# -*- coding: utf-8 -*-
import telegram
from flask import json
import os
import random
from quran_subscriptions_db import QuranSubscriptionsDB
from dotenv import load_dotenv
import sys

if len(sys.argv) < 1:
    print("Please pass home directory as argument")
    exit(0)

# load env
project_home = sys.argv[0]
load_dotenv(os.path.join(project_home, '.env'))

WORD_BASE_URL = "http://uxquran.com/apps/quran-ayat/"

# The folder path containing the resource files
STATIC_FOLDER = os.getenv("STATIC_FOLDER")

# Telegram token
TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = telegram.Bot(TOKEN)

subscriptionsDb = QuranSubscriptionsDB(os.path.join(STATIC_FOLDER, "daily.sqlite"))


def get_random_indices():
    json_data = open(os.path.join(STATIC_FOLDER, "surahlist.json"), "r")
    data = json.load(json_data)
    surah = random.randint(0, 113)
    ayat = random.randint(0, data[surah]["total_verses"]-1)
    return surah, ayat, data[surah]["transliteration_en"]


def get_ayat_ar(surah, ayat):
    json_data = open(os.path.join(STATIC_FOLDER, "quran-ar.json"), "r")
    data = json.load(json_data)
    if surah > 114 or surah == 114:
        return "Invalid surah number. Please send a surah number between 1 and 114."
    if ayat > len(data["quran"]["sura"][surah]["aya"]) or ayat == len(data["quran"]["sura"][surah]["aya"]):
        surahIndex = surah + 1
        return "Invalid ayat number. Surah {} has only {} ayats".format(surahIndex, len(data["quran"]["sura"][surah]["aya"]))
    else:
        return data["quran"]["sura"][surah]["aya"][ayat]["text"]

def get_ayat_en(surah, ayat):
    json_data = open(os.path.join(STATIC_FOLDER, "haleem.json"), "r")
    data = json.load(json_data)
    if surah > 114 or surah == 114:
        return "Invalid surah number. Please send a surah number between 1 and 114."
    if ayat > len(data["quran"]["sura"][surah]["aya"]) or ayat == len(data["quran"]["sura"][surah]["aya"]):
        surahIndex = surah + 1
        return "Invalid ayat number. Surah {} has only {} ayats".format(surahIndex, len(data["quran"]["sura"][surah]["aya"]))
    else:
        return data["quran"]["sura"][surah]["aya"][ayat]["text"]

# main

chat_ids = subscriptionsDb.select_all()
if len(chat_ids) > 0:
    for chat_id in chat_ids:
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



