from telebot.callback_data import CallbackData


find_train_form_factory = CallbackData('id',
                                       prefix='find_train_form')

FIND_TRAIN_FORM_KEYS = [
    {'id': '0', 'name': 'Дата отправления',
     'support_text': 'Введите дату отправления по МСК в формате ДД.ММ.ГГГГ',
     'step': 0},

    {'id': '1', 'name': 'Номер поезда',
     'support_text': 'Введите номер поезда (русские буквы)',
     'step': 1},
]