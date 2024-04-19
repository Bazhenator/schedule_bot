from aiogram import types


def keyboard(buttons):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
    buttons = list(buttons)
    keyboard.add(*buttons)
    return keyboard


def inline_keyboard():
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    next_button = types.InlineKeyboardButton(text="==>", callback_data="nextBtn")
    prev_button = types.InlineKeyboardButton(text="<==", callback_data="prevBtn")
    keyboard.row(prev_button, next_button)
    return keyboard