import time

import telebot
from telebot import types
import requests

import keyboards
from helper import CategoriesCallbackFilter
from markups import base_markup

bot = telebot.TeleBot("5410238338:AAE24dH_PdOTpQEfjVeGFaKhNg3XTwwCZyI")

temp_input = {}


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     "Добро пожаловать!",
                     reply_markup=base_markup())


@bot.message_handler()
def word_handler(message):
    if message.text == "Найти поезд":
        sent = bot.send_message(message.chat.id,
                                "Отправьте дату отправления по МСК в формате ДД.ММ.ГГГГ")
        bot.register_next_step_handler(sent,
                                       set_date)

    elif message.text == "Избранное":
        pass


# TODO Delete template
def set_date(message):
    temp_input.update({message.chat.id: {
        'date': "13.01.2023",  # message.text,
    }})
    sent = bot.send_message(message.chat.id,
                            "Отправьте номер поезда")
    bot.register_next_step_handler(sent,
                                   set_train)


def set_train(message):
    """Set train number in temp input list"""
    temp_input[message.chat.id]['train'] = "602НА"  # message.text
    display_cars(message)


def display_cars(message):
    # TODO write display cars
    set_stops_and_cars(message.chat.id,
                       temp_input[message.chat.id]['date'],
                       temp_input[message.chat.id]['train'],
                       )
    numbers = ""
    for k in temp_input[message.chat.id]['cars'].keys():
        numbers += str(k) + ", "
    ans = f"""
    Выберете из найденых вагонов:
{numbers}
И отправьте его.
    """
    print(temp_input[message.chat.id]['cars'])

    bot.send_message(message.chat.id,
                     text=ans)


def set_stops_and_cars(user_id, date, train):
    stops = get_stops_info(date,
                           train)
    temp_input[user_id]['stops'] = stops
    print("get_stops_info: Success")

    time.sleep(1)

    cars = get_cars_info(user_id, date, train, stops)
    temp_input[user_id]['cars'] = cars
    print("get_cars_info: Success")


def get_stops_info(date, train):
    params = {"STRUCTURE_ID": 704,
              "trainNumber": train,
              "depDate": date}
    headers = {'Host': 'pass.rzd.ru',
               'User-Agent': 'Mozila 5',
               'Accept': '*/*',
               'Accept-Encoding': 'gzip, deflate, br',
               'Connection': 'keep-alive'}

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


def get_cars_info(user_id: int, date: str, train: str, stops) -> dict:
    """
    :param user_id: user chat od
    :param date: date of departure
    :param train: train number
    :param stops: information about stops in format
    {
    :return: dict of cars

        between 1-2 station         between 5-6 station
    {car3: [[1,2,4,5],[4,3,2,3,5,],[...],[...],[...],[...],[...]]}
    """
    r = {}
    for i in range(0, len(stops) - 1):
        bot.send_message(user_id,
                         f"В процессе: {stops[i]['station']['name']} - {stops[i+1]['station']['name']}")
        params = {'layer_id': 5764,
                  'dir': 0,
                  'code0': stops[i]['station']['code'],
                  'code1': stops[i+1]['station']['code'],
                  'dt0': stops[i]['depTimeMSK'][:10].replace('-', '.'),
                  # 'time0': stops[i]['depTimeMSK'][-5:],
                  'tnum0': train
                  }
        headers = {'Host': 'pass.rzd.ru',
                   'User-Agent': 'Mozila 5',
                   'Accept': '*/*',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Connection': 'keep-alive'}

        s = requests.Session()
        res = s.get("https://pass.rzd.ru/timetable/public/",
                    params=params,
                    headers=headers).json()
        print(f"RID response: {res}")

        time.sleep(1)
        params['rid'] = res['RID']
        headers['Cookie'] = f"JSESSIONID={s.cookies['JSESSIONID']};" \
                            f" session-cookie={s.cookies['session-cookie']}"
        res = s.get("https://pass.rzd.ru/timetable/public/",
                           params=params,
                           headers=headers)
        # time.sleep(1)
        if res.status_code != 200:
            continue
        print(f"Cars res: {res}")
        print(res.json())
        cars = res.json()["lst"][0]["cars"]

        for car in cars:
            if car["cnumber"] in r:
                r[car["cnumber"]][i] = calc_free_places(car['places'])
            else:
                r[car["cnumber"]] = [[] for k in range(0, len(stops) - 1)]
                r[car["cnumber"]][i] = calc_free_places(car['places'])

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

            for j in range(int(a), int(b)+1):
                res.append(str(j).zfill(3))
        else:
            a = source[i]
            if 1040 <= ord(a[0]) <= 1071:
                a = a[1:]
            if 1040 <= ord(a[-1]) <= 1071:
                a = a[0:-1]
            res.append(a)

    return res


@bot.callback_query_handler(func=None,
                            config=keyboards.places_factory.filter())
def seat_callback(call: types.CallbackQuery):
    callback_data: dict = keyboards.places_factory.parse(
        callback_data=call.data)
    data = callback_data["data"]
    print(data)


bot.add_custom_filter(CategoriesCallbackFilter())
bot.polling(none_stop=True)
