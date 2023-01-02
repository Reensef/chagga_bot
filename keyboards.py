from telebot import types
from telebot.callback_data import CallbackData

places_factory = CallbackData('data',
                            prefix='seat')


def places(car_type, car_number):
    markup = types.InlineKeyboardMarkup(row_width=4)
    for i in range(1, 57, 4):
        markup.add(
            types.InlineKeyboardButton(
                text=i,
                callback_data=places_factory.new(data=f"{car_number}_{i}")
            ),
            types.InlineKeyboardButton(
                text=i+1,
                callback_data=places_factory.new(data=f"{car_number}_{i+1}")
            ),
            types.InlineKeyboardButton(
                text=i+2,
                callback_data=places_factory.new(data=f"{car_number}_{i+2}")
            ),
            types.InlineKeyboardButton(
                text=i+3,
                callback_data=places_factory.new(data=f"{car_number}_{i+3}")
            ),
        )

    return markup