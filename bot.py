import telebot
from telebot import types

import config

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    shedule_search_button = types.InlineKeyboardButton("Найти расписание по группе", callback_data='shedule_search')
    spbstu_button = types.InlineKeyboardButton("Сайт с расписанием", url='https://ruz.spbstu.ru/')

    markup.add(shedule_search_button)
    markup.add(spbstu_button)

    bot.send_message(message.chat.id, "Привет, {0.first_name}!".format(message.from_user), reply_markup=markup)


bot.polling(none_stop=True)
