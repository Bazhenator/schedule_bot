import telebot

kb_start = telebot.types.InlineKeyboardMarkup()
shedule_search_button = telebot.types.InlineKeyboardButton(text="Найти расписание по группе",
                                                           callback_data='shedule_search')
spbstu_button = telebot.types.InlineKeyboardButton(text="Сайт с расписанием",
                                                   url='https://ruz.spbstu.ru/')
kb_start.add(shedule_search_button, spbstu_button)
