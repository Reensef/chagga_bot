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
    ask_train(message)


def ask_train(message):
    sent = bot.send_message(message.chat.id,
                            "Отправьте номер поезда")
    bot.register_next_step_handler(sent,
                                   set_train_and_display_cars)


def set_train_and_display_cars(message):
    """Set train number in temp input list"""
    temp_input[message.chat.id]['train'] = "602НА"  # message.text
    display_cars(message)


def display_cars(message):
    # TODO write display cars
    # set_stops_and_cars(message.chat.id,
    #                    temp_input[message.chat.id]['date'],
    #                    temp_input[message.chat.id]['train'],
    #                    )
    stops = get_stops_info(temp_input[message.chat.id]['date'],
                           temp_input[message.chat.id]['train'])
    if not stops:
        bot.send_message(message.chat.id, "Ошибка при получении списка станций")
        return

    cars = get_cars_info(message.chat.id,
                         temp_input[message.chat.id]['train'],
                         stops)
    print(cars)
    for car_key in cars.keys():
        print(car_key)
        ans = f"Вагон номер {car_key}\n"
        ans += "===============\n"
        for stop_id in range(len(stops) - 1):
            ans += f"{stops[stop_id]['station']['name']}-{stops[stop_id+1]['station']['name']}:\n"
            ans += f"{cars[car_key][stop_id]}\n"
        bot.send_message(message.chat.id, ans)


def set_stops_and_cars(user_id, date, train):
    stops = get_stops_info(date,
                           train)
    temp_input[user_id]['stops'] = stops
    print("get_stops_info: Success")

    time.sleep(1)

    if not stops:
        bot.send_message(user_id, "Ошибка при получении списка станций")
    else:
        cars = get_cars_info(user_id, train, stops)
        temp_input[user_id]['cars'] = cars
        print("get_cars_info: Success")


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

    except:
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
                         f"В процессе: {stops[number_of_station]['station']['name']} - {stops[number_of_station+1]['station']['name']}")

        params = {'layer_id': 5764,
                  'dir': 0,
                  'code0': stops[number_of_station]['station']['code'],
                  'code1': stops[number_of_station+1]['station']['code'],
                  'dt0': stops[number_of_station]['depTimeMSK'][:10].replace('-', '.'),
                  'tnum0': train}

        headers = {'Host': 'pass.rzd.ru',
                   'User-Agent': 'Mozila 5',
                   'Accept': '*/*',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Connection': 'keep-alive'}

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

        # time.sleep(1)

        if res.status_code != 200:
            continue

        # print(f"Cars res: {res}")
        # print(res.json())
        cars = res.json()["lst"][0]["cars"]

        for car in cars:
            if car["cnumber"] in r:
                r[car["cnumber"]][number_of_station] = calc_free_places(car['places'])
            else:
                r[car["cnumber"]] = [[] for k in range(0, len(stops) - 1)]
                r[car["cnumber"]][number_of_station] = calc_free_places(car['places'])

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


bot.add_custom_filter(CategoriesCallbackFilter())
bot.polling(none_stop=True)
