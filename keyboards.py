import telebot

kb_main = telebot.types.InlineKeyboardMarkup()
shedule_search_button = telebot.types.InlineKeyboardButton(text="Найти расписание по группе",
                                                           callback_data='shedule_search')
spbstu_button = telebot.types.InlineKeyboardButton(text="Сайт с расписанием",
                                                   url='https://ruz.spbstu.ru/')
kb_main.add(shedule_search_button, spbstu_button)

kb_menu = telebot.types.InlineKeyboardMarkup()
menu_button = telebot.types.InlineKeyboardButton(text="Меню",
                                                 callback_data='main_menu')
kb_menu.add(menu_button)
