# Modules import
import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime
import pytz

# Header files
import parcing
from sqlighter import SQLighter
from keyboard import keyboard, inline_keyboard
import encode
# Logs level
logging.basicConfig(level=logging.INFO)

# Bot initialization
bot = Bot(token='$TOKEN')
dp = Dispatcher(bot)

# Base initialisation
db = SQLighter('telegrambot_database_new.db')


# First initialization
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if not db.subscriber_exists(message.from_user.id):
        db.add_subscriber(message.from_user.id)
    await message.answer('Вы успешно начали работу с ботом')
    await message.answer('Выберете институт, в котором Вы учитесь',
                         reply_markup=keyboard(parcing.universities().keys()))


@dp.message_handler(lambda message: message.text in list(parcing.universities().keys()))
async def choose_group(message: types.Message):
    group_link = parcing.universities()[message.text]
    db.update_link(message.from_user.id, 'week_url', group_link)
    await message.answer('Выберете группу, в которой Вы учитесь',
                         reply_markup=keyboard(parcing.groups(group_link).keys()))


@dp.message_handler(lambda x: x.text in list(parcing.groups(db.get_link(x.from_user.id, 'week_url')).keys()))
async def schedule(message: types.Message):
    schedule_url = parcing.groups(db.get_link(message.from_user.id, 'week_url'))[message.text] + '?'
    weekday = datetime.now(pytz.timezone('Europe/Moscow')).weekday()
    db.update_link(message.from_user.id, 'week_url', schedule_url)
    db.update_weekday(message.from_user.id, weekday)
    parcing.update_week_urls(message.from_user.id, schedule_url)
    parcing.update_encoded_week(message.from_user.id)
    await message.answer('Ваше расписание в процессе загрузки...',
                         reply_markup=types.ReplyKeyboardRemove())
    msg = parcing.parse_week(message.from_user.id, weekday)[0]
    await bot.send_message(message.from_user.id,
                           msg,
                           reply_markup=inline_keyboard(), parse_mode=types.ParseMode.MARKDOWN)


@dp.callback_query_handler(text="nextBtn")
async def switch_next_week(message: types.Message):
    weekday = db.get_weekday(message.from_user.id) + 1
    msg = parcing.parse_week(message.from_user.id, weekday)[0]
    await bot.edit_message_text(msg, message.from_user.id,
                                message.message.message_id,
                                reply_markup=inline_keyboard(), parse_mode=types.ParseMode.MARKDOWN)
    need_to_switch = parcing.parse_week(message.from_user.id, weekday)[1]
    db.update_weekday(message.from_user.id, weekday)
    if need_to_switch:
        db.update_link(message.from_user.id, 'week_url',
                       db.get_link(message.from_user.id, 'prev_week_url' if need_to_switch == -1 else 'next_week_url'))
        asyncio.create_task(parcing.update_encoded_week(message.from_user.id))


@dp.callback_query_handler(text="prevBtn")
async def switch_prev_week(message: types.Message):
    schedule_url = db.get_link(message.from_user.id, 'week_url')
    weekday = db.get_weekday(message.from_user.id) - 1
    msg = parcing.parse_week(message.from_user.id, weekday)[0]
    await bot.edit_message_text(msg, message.from_user.id,
                                message.message.message_id,
                                reply_markup=inline_keyboard(), parse_mode=types.ParseMode.MARKDOWN)
    need_to_switch = parcing.parse_week(message.from_user.id, weekday)[1]
    db.update_weekday(message.from_user.id, weekday)
    if need_to_switch:
        db.update_link(message.from_user.id, 'week_url',
                       db.get_link(message.from_user.id, 'prev_week_url' if need_to_switch == -1 else 'next_week_url'))
        asyncio.create_task(parcing.update_encoded_week(message.from_user.id))


@dp.callback_query_handler(text="delete")
async def delete_message(message: types.Message):
    await bot.delete_message(message.from_user.id, message.message.message_id)


@dp.message_handler(commands=['subs_number'])
async def start(message: types.Message):
    await message.answer(str(len(db.get_subscriptions())))


async def scheduled(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        # получаем список подписчиков бота
        subscriptions = db.get_subscriptions()
        for user_id in subscriptions:
            parcing.update_encoded_week(user_id)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # loop.create_task(scheduled(10))  # Каждые 10 минут проверка
    executor.start_polling(dp, skip_updates=True)
