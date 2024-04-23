import logging

import telebot

from datetime import datetime

import requests

from states import weekdays, months
from text import text_messages
from keyboard import kb_main, kb_menu
import config

bot = telebot.TeleBot(config.TOKEN)
logger = telebot.logger
telebot.logger.setLevel(logging.INFO)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.delete_message(chat_id=message.chat.id,
                       message_id=message.message_id)
    bot.send_message(chat_id=message.from_user.id,
                     text=text_messages['intro'].format(message.from_user),
                     reply_markup=kb_main)


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.delete_message(chat_id=message.chat.id,
                       message_id=message.message_id)
    bot.send_message(chat_id=message.chat.id,
                     text=text_messages['info'], parse_mode='HTML',
                     reply_markup=kb_menu)


@bot.callback_query_handler(func=lambda call: call.data.startswith('main_menu'))
def show_main_menu(call):
    bot.delete_message(chat_id=call.message.chat.id,
                       message_id=call.message.message_id)
    bot.send_message(chat_id=call.message.chat.id,
                     text=text_messages['choose_action'],
                     reply_markup=kb_main)


@bot.callback_query_handler(func=lambda call: call.data.startswith('schedule_search'))
def schedule_search(call):
    bot.delete_message(chat_id=call.message.chat.id,
                       message_id=call.message.message_id)
    if call.data.startswith('schedule_search_by_group'):
        msg = bot.send_message(chat_id=call.message.chat.id,
                               text=text_messages['enter_group'],
                               reply_markup=kb_menu)
        bot.register_next_step_handler(message=msg,
                                   callback=schedule_search_by_group)
    elif call.data.startswith('schedule_search_by_teacher'):
        msg = bot.send_message(chat_id=call.message.chat.id,
                               text=text_messages['enter_teacher'],
                               reply_markup=kb_menu)
        bot.register_next_step_handler(message=msg,
                                       callback=schedule_search_by_teacher)


def schedule_search_by_teacher(message):
    if message.text == '/start':
        return start_message(message)
    if message.text == '/help':
        return help_message(message)

    bot.delete_message(chat_id=message.chat.id,
                       message_id=message.message_id)

    json_data = requests.get(f"https://ruz.spbstu.ru/api/v1/ruz/search/teachers?q="
                             f"{message.text.replace(' ', '%20')}").json()
    teachers_data = json_data['teachers']
    if not teachers_data:
        bot.send_message(chat_id=message.chat.id,
                         text=text_messages['wrong_teacher'],
                         reply_markup=kb_menu)
        return bot.register_next_step_handler(message, schedule_search_by_teacher)

    teacher_id = teachers_data[0]['id']
    json_data = requests.get(f"https://ruz.spbstu.ru/api/v1/ruz/teachers/{teacher_id}/scheduler").json()

    week_data = json_data['week']
    bot.send_message(chat_id=message.chat.id,
                     text=f"Неделя: {week_data['date_start']} - {week_data['date_end']}")

    days_data = json_data['days']
    lessons_str = ''
    for day in days_data:
        date = datetime.strptime(day['date'], "%Y-%m-%d")

        lessons_str += "========================================\n"
        lessons_str += f"*{date.day} {months.get(date.month)}, {weekdays.get(day['weekday'])}*\n"
        lessons_str += "========================================\n"

        lessons = day['lessons']
        for lesson in lessons:
            lessons_str += f"⏱️ _{lesson['time_start']} - {lesson['time_end']}_\n"
            lessons_str += f"📚 {lesson['typeObj']['name']}\n"
            lessons_str += f"📖 {lesson['subject']}\n"
            lessons_str += f"🏫 {lesson['auditories'][0]['building']['name']}, {lesson['auditories'][0]['name']}\n"

            if lesson['teachers']:
                lessons_str += f"🧑‍🏫 {lesson['teachers'][0]['full_name']}\n"
            if lesson['lms_url']:
                lessons_str += f"[🛜 СДО]({lesson['lms_url']})\n"
            lessons_str += "\n"

    bot.send_message(chat_id=message.chat.id,
                     text=lessons_str,
                     parse_mode="Markdown",
                     reply_markup=kb_menu)


def schedule_search_by_group(message):
    if message.text == '/start':
        return start_message(message)
    if message.text == '/help':
        return help_message(message)

    bot.delete_message(chat_id=message.chat.id,
                       message_id=message.message_id)

    json_data = requests.get(f"https://ruz.spbstu.ru/api/v1/ruz/search/groups?q={message.text}").json()
    if not json_data['groups']:
        bot.send_message(chat_id=message.chat.id,
                         text=text_messages['wrong_group'],
                         reply_markup=kb_menu)
        return bot.register_next_step_handler(message, schedule_search_by_group)

    group_data = json_data['groups']
    group_id = group_data[0]['id']

    json_data = requests.get(f"https://ruz.spbstu.ru/api/v1/ruz/scheduler/{group_id}").json()
    week_data = json_data['week']
    week_data = ''.join(reversed(week_data))
    bot.send_message(chat_id=message.chat.id,
                     text=f"Неделя: {week_data['date_start']} - {week_data['date_end']}")

    days_data = json_data['days']
    lessons_str = ''
    for day in days_data:
        date = datetime.strptime(day['date'], "%Y-%m-%d")

        lessons_str += "========================================\n"
        lessons_str += f"*{date.day} {months.get(date.month)}, {weekdays.get(day['weekday'])}*\n"
        lessons_str += "========================================\n"

        lessons = day['lessons']
        for lesson in lessons:
            lessons_str += f"⏱️ _{lesson['time_start']} - {lesson['time_end']}_\n"
            lessons_str += f"📚 {lesson['typeObj']['name']}\n"
            lessons_str += f"📖 {lesson['subject']}\n"
            lessons_str += f"🏫 {lesson['auditories'][0]['building']['name']}, {lesson['auditories'][0]['name']}\n"

            if lesson['teachers']:
                lessons_str += f"🧑‍🏫 {lesson['teachers'][0]['full_name']}\n"
            if lesson['lms_url']:
                lessons_str += f"[🛜 СДО]({lesson['lms_url']})\n"
            lessons_str += "\n"

    bot.send_message(chat_id=message.chat.id,
                     text=lessons_str,
                     parse_mode="Markdown",
                     reply_markup=kb_menu)


def main():
    bot.set_my_commands([
        telebot.types.BotCommand("/start", "Основное меню"),
        telebot.types.BotCommand("/help", "Описание бота и команд")
    ])
    bot.polling(none_stop=True)


if __name__ == '__main__':
    main()
