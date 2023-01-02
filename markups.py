from telebot import types


def base_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                       row_width=1)
    markup.add(
        types.KeyboardButton("Найти поезд"),
        types.KeyboardButton("Избранное")
    )

    return markup


