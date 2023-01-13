from telebot import types

import keyboards_data


def base_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                       row_width=1)
    markup.add(
        types.KeyboardButton("Найти поезд")
    )

    return markup


def find_train_form():
    """
    :return: markup object for find_train_form
    """
    markup = types.InlineKeyboardMarkup()
    for key in keyboards_data.FIND_TRAIN_FORM_KEYS:
        markup.add(
            types.InlineKeyboardButton(
                text=key['name'],
                callback_data=keyboards_data.find_train_form_factory
                .new(id=key['id'])
            )
        )

    # specials keys with special callback
    markup.add(

        types.InlineKeyboardButton(
            text="Найти",
            callback_data="find_train_form_send"
        ),

        types.InlineKeyboardButton(
            text="Отмена",
            callback_data="find_train_form_cancel"
        )

    )

    return markup


def choose_car(cars: dict):
    markup = types.InlineKeyboardMarkup()

    for car in cars.keys():
        markup.add(
            types.InlineKeyboardButton(
                text=f'{car}',
                callback_data=keyboards_data.choose_car_factory
                .new(car)
            )
        )

    markup.add(
        types.InlineKeyboardButton(
            text="Выход",
            callback_data="car_choose_back"
        )
    )

    return markup


def choose_place(chosen_place):
    markup = types.InlineKeyboardMarkup(row_width=7)

    for place in range(1, 57, 7):
        markup.add(
            types.InlineKeyboardButton(
                text=f"({place})" if place == int(chosen_place) else f"{place}",
                callback_data=keyboards_data.choose_places_factory
                .new(str(place))
            ),
            types.InlineKeyboardButton(
                text=f"({place+1})" if place+1 == int(
                    chosen_place) else f"{place+1}",
                callback_data=keyboards_data.choose_places_factory
                .new(str(place+1))
            ),
            types.InlineKeyboardButton(
                text=f"({place+2})" if place+2 == int(
                    chosen_place) else f"{place+2}",
                callback_data=keyboards_data.choose_places_factory
                .new(str(place+2))
            ),
            types.InlineKeyboardButton(
                text=f"({place+3})" if place+3 == int(
                    chosen_place) else f"{place+3}",
                callback_data=keyboards_data.choose_places_factory
                .new(str(place+3))
            ),
            types.InlineKeyboardButton(
                text=f"({place+4})" if place+4 == int(
                    chosen_place) else f"{place+4}",
                callback_data=keyboards_data.choose_places_factory
                .new(str(place+4))
            ),
            types.InlineKeyboardButton(
                text=f"({place+5})" if place+5 == int(
                    chosen_place) else f"{place+5}",
                callback_data=keyboards_data.choose_places_factory
                .new(str(place+5))
            ),
            types.InlineKeyboardButton(
                text=f"({place+6})" if place+6 == int(
                    chosen_place) else f"{place+6}",
                callback_data=keyboards_data.choose_places_factory
                .new(str(place+6))
            )
        )

    markup.add(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data="place_choose_back"
        )
    )

    return markup