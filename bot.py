import requests
import telebot

import config
from keyboards import kb_start

bot = telebot.TeleBot(config.TOKEN)

weekdays = {
    1: 'пн',
    2: 'вт',
    3: 'ср',
    4: 'чт',
    5: 'пт',
    6: 'сб',
    7: 'вс',
}


@bot.message_handler(commands=['start'])
def start_messages(message):
    bot.delete_message(message.chat.id, message.message_id)
    bot.send_message(message.from_user.id, "Привет, {0.first_name}!".format(message.from_user), reply_markup=kb_start)


@bot.callback_query_handler(func=lambda call: call.data.startswith('shedule_search'))
def shedule_search(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    msg = bot.send_message(call.message.chat.id, text="Введи номер своей группы")
    bot.register_next_step_handler(msg, shedule_search_by_group)


def shedule_search_by_group(message):
    bot.delete_message(message.chat.id, message.message_id)

    json_data = requests.get("https://ruz.spbstu.ru/api/v1/ruz/search/groups?q=" + message.text).json()
    group_data = json_data['groups']
    group_id = group_data[0]['id']

    json_data = requests.get("https://ruz.spbstu.ru/api/v1/ruz/scheduler/" + str(group_id)).json()
    week_data = json_data['week']
    bot.send_message(message.chat.id, text=f"Неделя: {week_data['date_start']} - {week_data['date_end']}")

    days_data = json_data['days']
    for day in days_data:
        lessons_str = ''
        lessons_str += f"{weekdays.get(day['weekday'])}\n"

        lessons = day['lessons']
        for lesson in lessons:
            lessons_str += f"{lesson['time_start']} - {lesson['time_end']}\n"
            lessons_str += f"*{lesson['subject']}*\n"
            lessons_str += f"{lesson['typeObj']['name']}\n"
            if lesson['teachers']:
                lessons_str += f"{lesson['teachers'][0]['full_name']}\n"
            if lesson['lms_url']:
                lessons_str += f"[СДО]({lesson['lms_url']})\n"
            lessons_str += "\n"
        bot.send_message(message.chat.id, text=lessons_str, parse_mode="Markdown")


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
