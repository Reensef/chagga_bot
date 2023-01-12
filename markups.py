from telebot import types

import keyboards_data


def base_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                       row_width=1)
    markup.add(
        types.KeyboardButton("Найти поезд"),
        types.KeyboardButton("Избранное")
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
