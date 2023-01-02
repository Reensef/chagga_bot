from telebot import types, AdvancedCustomFilter
from telebot.callback_data import CallbackDataFilter


class CategoriesCallbackFilter(AdvancedCustomFilter):
    key = 'config'

    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)