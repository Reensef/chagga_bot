import os

import sys

import time

import telebot
from requests import ReadTimeout
from telebot import types
import requests

import keyboards_data
import markups
import strings
from helper import CategoriesCallbackFilter

bot = telebot.TeleBot("5410238338:AAE24dH_PdOTpQEfjVeGFaKhNg3XTwwCZyI")

temp_input = {}


@bot.message_handler(commands=['start'])
def start(message):
    form = {'date': '',
            'train': '',
            'step': '',
            'cars': '',
            'car_number': ''}
    bot.send_message(message.chat.id,
                     "Добро пожаловать!",
                     reply_markup=markups.base_markup())


# @bot.message_handler()
# def word_handler(message):
#     if message.text == "Найти поезд":
#         sent = bot.send_message(message.chat.id,
#                                 "Отправьте дату отправления по МСК в формате ДД.ММ.ГГГГ")
#         bot.register_next_step_handler(sent,
#                                        set_date)
#
#     elif message.text == "Избранное":
#         pass

@bot.message_handler()
def main_handler(message):
    if message.text == "Найти поезд":
        form = {'date': '',
                'train': '',
                'step': '',
                'cars': '',
                'car_number': ''}
        temp_input[message.chat.id] = form

        bot.send_message(message.chat.id,
                         text="Заполните форму",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(message.chat.id,
                         text=strings.find_train_form_text(form),
                         reply_markup=markups.find_train_form())

    if message.text == "Избранное":
        bot.send_message(message.chat.id,
                         "Избранное")


@bot.callback_query_handler(func=None,
                            config=keyboards_data.find_train_form_factory
                            .filter())
def input_find_train_form(call: types.CallbackQuery):
    call_data: dict = keyboards_data.find_train_form_factory \
        .parse(callback_data=call.data)
    key_id = int(call_data['id'])
    support_text = keyboards_data.FIND_TRAIN_FORM_KEYS[key_id]['support_text']

    sent = bot.edit_message_text(chat_id=call.message.chat.id,
                                 message_id=call.message.message_id,
                                 text=support_text)

    temp_input[call.message.chat.id]["step"] = \
        keyboards_data.FIND_TRAIN_FORM_KEYS[key_id]['step']

    bot.register_next_step_handler(sent, set_find_train_form)


def set_find_train_form(message):
    form = temp_input[message.chat.id]
    form[form['step']] = message.text

    temp_input[message.chat.id] = form

    bot.send_message(message.chat.id,
                     text=strings.find_train_form_text(form),
                     reply_markup=markups.find_train_form())


@bot.callback_query_handler(func=lambda c: c.data == 'find_train_form_cancel')
def cancel_train_form(call: types.CallbackQuery):
    temp_input.pop(call.message.chat.id)

    bot.delete_message(chat_id=call.message.chat.id,
                       message_id=call.message.message_id)
    bot.send_message(call.message.chat.id,
                     text="Поиск отменен",
                     reply_markup=markups.base_markup())


@bot.callback_query_handler(func=lambda c: c.data == 'find_train_form_send')
def send_train_form(call: types.CallbackQuery):
    bot.delete_message(chat_id=call.message.chat.id,
                       message_id=call.message.message_id)

    display_cars(call.message)


def display_cars(message: types.Message):
    stops = get_stops_info(temp_input[message.chat.id]['date'],
                           temp_input[message.chat.id]['train'])
    if not stops:
        bot.send_message(message.chat.id,
                         "‼️Поезд не найден‼️")
        bot.send_message(message.chat.id,
                         text=strings.find_train_form_text(
                             temp_input[message.chat.id]
                         ),
                         reply_markup=markups.find_train_form())

        return

    temp_input[message.chat.id]['stops'] = stops

    cars = get_cars_info(message.chat.id,
                         temp_input[message.chat.id]['train'],
                         stops)

    temp_input[message.chat.id]['cars'] = cars

    bot.send_message(message.chat.id,
                     text="Выберите вагон",
                     reply_markup=markups.choose_car(cars))


@bot.callback_query_handler(func=None,
                            config=keyboards_data.choose_car_factory.filter())
def display_init_places_information(call: types.CallbackQuery):
    call_data: dict = keyboards_data.choose_car_factory.parse(
        callback_data=call.data)
    car_number = call_data['number']
    temp_input[call.message.chat.id]['car_number'] = car_number

    bot.delete_message(chat_id=call.message.chat.id,
                       message_id=call.message.message_id)

    bot.send_message(
        call.message.chat.id,
        text=strings.places_text(
            temp_input[call.message.chat.id]['stops'],
            temp_input[call.message.chat.id]['cars'][car_number],
            car_number, '1'), parse_mode='Markdown',
        reply_markup=markups.choose_place('1'))


@bot.callback_query_handler(func=None,
                            config=keyboards_data.choose_places_factory.filter())
def display_places_information(call: types.CallbackQuery):
    call_data: dict = keyboards_data.choose_places_factory.parse(
        callback_data=call.data)
    chosen_place = call_data['place']
    car_number = temp_input[call.message.chat.id]['car_number']

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=strings.places_text(
            temp_input[call.message.chat.id]['stops'],
            temp_input[call.message.chat.id]['cars'][car_number],
            car_number=car_number,
            chosen_place=chosen_place
        ), parse_mode="Markdown",
        reply_markup=markups.choose_place(chosen_place))


@bot.callback_query_handler(func=lambda c: c.data == 'place_choose_back')
def place_choose_back(call: types.CallbackQuery):
    bot.delete_message(chat_id=call.message.chat.id,
                       message_id=call.message.message_id)

    bot.send_message(call.message.chat.id,
                     text="Выберите вагон",
                     reply_markup=markups.choose_car(
                         temp_input[call.message.chat.id]['cars']
                     ))


@bot.callback_query_handler(func=lambda c: c.data == 'car_choose_back')
def car_choose_back(call: types.CallbackQuery):
    bot.delete_message(chat_id=call.message.chat.id,
                       message_id=call.message.message_id)

    bot.send_message(call.message.chat.id,
                     text="Поиск отменен",
                     reply_markup=markups.base_markup())


def get_stops_info(date: str, train: str) -> list:
    """
    :param date: date of departure
    :param train: train number
    :return: stops information in format
    [{
        "arvTime": null,
        "depTime": "13-01-2023 20:17",
        "arvTimeMSK": null,
        "depTimeMSK": "13-01-2023 16:17",
        "diffTimeInHours": 4,
        "waitingTime": null,
        "station": {
            "name": "БИЙСК",
            "engName": "BIISK",
            "code": 2044720
        }
    }, .... ]
    """

    params = {"STRUCTURE_ID": 704,
              "trainNumber": train,
              "depDate": date}
    headers = {'Host': 'pass.rzd.ru',
               'User-Agent': 'Mozila 5',
               'Accept': '*/*',
               'Accept-Encoding': 'gzip, deflate, br',
               'Connection': 'keep-alive'}

    try:
        s = requests.Session()
        res = s.get("https://pass.rzd.ru/ticket/services/route/basicRoute",
                    params=params,
                    headers=headers).json()

        time.sleep(1)

        params['rid'] = res['RID']
        headers['Cookie'] = f"JSESSIONID={s.cookies['JSESSIONID']};" \
                            f" session-cookie={s.cookies['session-cookie']}"

        res = s.get("https://pass.rzd.ru/ticket/services/route/basicRoute",
                    params=params,
                    headers=headers).json()

        return res['data']['routes'][0]['stops']

    except Exception as e:
        print(e)
        return []


def get_cars_info(user_id: int, train: str, stops) -> dict:
    """
    :param user_id: user chat od
    :param train: train number
    :param stops: information about stops see: get_stops_info()
    :return: dict of cars

        between 1-2 station         between 5-6 station
    {3: [[1,2,4,5],[4,3,2,3,5,],[...],[...],[...],[...],[...]],
    5: [[][][][]...]}
    """
    r = {}
    for number_of_station in range(0, len(stops) - 1):
        bot.send_message(user_id,
                         f"В процессе: {stops[number_of_station]['station']['name']} - {stops[number_of_station + 1]['station']['name']}")

        params = {'layer_id': 5764,
                  'dir': 0,
                  'code0': stops[number_of_station]['station']['code'],
                  'code1': stops[number_of_station + 1]['station']['code'],
                  'dt0': stops[number_of_station]['depTimeMSK'][:10].replace(
                      '-', '.'),
                  'tnum0': train}

        headers = {'Host': 'pass.rzd.ru',
                   'User-Agent': 'Mozila 5',
                   'Accept': '*/*',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Connection': 'keep-alive'}
        try:
            s = requests.Session()
            res = s.get("https://pass.rzd.ru/timetable/public/",
                        params=params,
                        headers=headers).json()
            # print(f"RID response: {res}")

            time.sleep(1)

            params['rid'] = res['RID']
            headers['Cookie'] = f"JSESSIONID={s.cookies['JSESSIONID']};" \
                                f" session-cookie={s.cookies['session-cookie']}"
            res = s.get("https://pass.rzd.ru/timetable/public/",
                        params=params,
                        headers=headers)

            # print(f"Cars res: {res}")
            # print(res.json())
            cars = res.json()["lst"][0]["cars"]

            for car in cars:
                if car["cnumber"] in r:
                    r[car["cnumber"]][number_of_station] = calc_free_places(
                        car['places'])
                else:
                    r[car["cnumber"]] = [[] for k in range(0, len(stops) - 1)]
                    r[car["cnumber"]][number_of_station] = calc_free_places(
                        car['places'])
        except Exception as e:
            print(e.with_traceback())
            bot.send_message(user_id, "Ошибка при получении вагона")

    return r


def calc_free_places(s: str) -> list:
    """
    :param s: string of places in format "004Ж,006-008С,011Ж,012Ж"
    :return: list of places ['004', '006', '007', '008', '011', '012']
    """
    if len(s) == 0:
        return []
    source = s.split(',')
    res = []

    for i in range(0, len(source)):
        if '-' in source[i]:
            target = source[i].split('-')
            a = target[0]
            b = target[1]
            if 1040 <= ord(a[0]) <= 1071:
                a = a[1:]
            if 1040 <= ord(a[-1]) <= 1071:
                a = a[0:-1]

            if 1040 <= ord(b[0]) <= 1071:
                b = b[1:]
            if 1040 <= ord(b[-1]) <= 1071:
                b = b[0:-1]

            for j in range(int(a), int(b) + 1):
                res.append(str(j).zfill(3))
        else:
            a = source[i]
            if 1040 <= ord(a[0]) <= 1071:
                a = a[1:]
            if 1040 <= ord(a[-1]) <= 1071:
                a = a[0:-1]
            res.append(a)

    return res


bot.add_custom_filter(CategoriesCallbackFilter())


try:
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
except (ConnectionError, ReadTimeout) as e:
    sys.stdout.flush()
    os.execv(sys.argv[0], sys.argv)
else:
    bot.infinity_polling(timeout=10, long_polling_timeout=5)