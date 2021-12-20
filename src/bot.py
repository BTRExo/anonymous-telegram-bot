import os

import telebot

bot = telebot.TeleBot(os.environ['BOT_TOKEN'], parse_mode='HTML')
