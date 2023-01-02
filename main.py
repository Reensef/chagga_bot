import telebot
from telebot import types
import requests

import keyboards
from helper import CategoriesCallbackFilter
from markups import base_markup

bot = telebot.TeleBot("5410238338:AAE24dH_PdOTpQEfjVeGFaKhNg3XTwwCZyI")


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     "Добро пожаловать!",
                     reply_markup=base_markup())


@bot.message_handler(commands=['r'])
def r(message):
    res = requests.get("https://pass.rzd.ru/timetable/public/?layer_id=5764&dir=0&code0=2044800&code1=2028170&dt0=04.01.2023&time0=21:01&tnum0=602НА")
    print(res)


@bot.message_handler()
def word_handler(message):
    if message.text == "Найти поезд":
        sent = bot.send_message(message.chat.id,
                                "Отправьте номер поезда.")
        bot.register_next_step_handler(sent,
                                       display_train)

    elif message.text == "Избранное":
        pass


def display_train(message):
    bot.send_message(message.chat.id,
                     text="this is a big text",
                     reply_markup=keyboards.places("seating", 7))


@bot.callback_query_handler(func=None,
                            config=keyboards.places_factory.filter())
def seat_callback(call: types.CallbackQuery):
    callback_data: dict = keyboards.places_factory.parse(
        callback_data=call.data)
    data = callback_data["data"]
    print(data)


bot.add_custom_filter(CategoriesCallbackFilter())
bot.polling(none_stop=True)
