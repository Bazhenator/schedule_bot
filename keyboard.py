import telebot

kb_main = telebot.types.InlineKeyboardMarkup()
group_schedule_search_button = telebot.types.InlineKeyboardButton(text="Найти расписание по группе",
                                                           callback_data='schedule_search_by_group')
teacher_schedule_search_button = telebot.types.InlineKeyboardButton(text="Найти расписание по преподавателю",
                                                                     callback_data='schedule_search_by_teacher')
spbstu_button = telebot.types.InlineKeyboardButton(text="Сайт с расписанием",
                                                   url='https://ruz.spbstu.ru/')
kb_main.add(group_schedule_search_button, teacher_schedule_search_button, spbstu_button)

kb_menu = telebot.types.InlineKeyboardMarkup()
menu_button = telebot.types.InlineKeyboardButton(text="Меню",
                                                 callback_data='main_menu')
kb_menu.add(menu_button)
