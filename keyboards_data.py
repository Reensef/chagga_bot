from telebot.callback_data import CallbackData

find_train_form_factory = CallbackData('id',
                                       prefix='find_train_form')

choose_car_factory = CallbackData('number',
                                  prefix='choose_car')

choose_places_factory = CallbackData('place',
                                     prefix='choose_place')

FIND_TRAIN_FORM_KEYS = [
    {'id': '0', 'name': 'Дата отправления',
     'support_text': 'Введите дату отправления по МСК в формате ДД.ММ.ГГГГ',
     'step': 'date'},

    {'id': '1', 'name': 'Номер поезда',
     'support_text': 'Введите номер поезда (русские буквы)',
     'step': 'train'},
]
