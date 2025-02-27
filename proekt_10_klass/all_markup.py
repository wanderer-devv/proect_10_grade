from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from requests_in_bd import RequestsInBD

yes_or_no_markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Да'), KeyboardButton(text='Нет')]], resize_keyboard=True, one_time_keyboard=True)

otmena_markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отмена')]], resize_keyboard=True, one_time_keyboard=True)

markup_of_notif_error = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Расписписание', url=r'https://sites.google.com/view/perspectiva99/%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F-%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0')]])

markup_of_opros = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Да', callback_data='yes_opros_work')],
                                                        [InlineKeyboardButton(text='Нет', callback_data='no_opros_work')]])

main_menu_for_error = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Прислать расписание моего класса')], 
                                        [KeyboardButton(text='Прислать расписание другого класса')], 
                                        [KeyboardButton(text='Подписаться на уведомления')]], resize_keyboard=True)

def return_main_markup(user_id):
    requestsInBD = RequestsInBD()
    notif = requestsInBD.get_notif(user_id=user_id)
    requestsInBD.close_bd()

    if notif:
        if notif == 1:
            sub_or_unsub = 'Отписаться от уведомлений'
        elif notif == 2:
            sub_or_unsub = 'Подписаться на уведомления'

        return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Прислать расписание моего класса')], 
                                                [KeyboardButton(text='Прислать расписание другого класса')], 
                                                [KeyboardButton(text='Изменить класс')], 
                                                [KeyboardButton(text=sub_or_unsub)]], resize_keyboard=True)
    elif not notif:
        return False