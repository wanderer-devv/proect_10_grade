from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from requests_in_bd import RequestsInBD
from requests_rasp import ClassOfGetRasp
from all_markup import otmena_markup, return_main_markup, markup_of_opros
from aiogram.client.default import DefaultBotProperties
import asyncio
import sys

requestsInBD = RequestsInBD()
classOfGetRasp = ClassOfGetRasp()

yes_or_no_dict = {'yes_opros_work': 'Да', 'no_opros_work': 'Нет'}

class user_states(StatesGroup):
    set_grade = State()
    other_class = State()
    new_class = State()
    anon_mes = State()


token = 'TOKEN_1' # тест
# token = 'TOKEN_2' # основа

bot = Bot(token=token, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

async def send_main_menu(message, text):
    main_menu = return_main_markup(message.from_user.id)
    check_us = requestsInBD.check(message.from_user.id)

    if main_menu and not check_us:
        await message.answer(text, reply_markup=main_menu)

################# /start ####################

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    check = requestsInBD.check(user_id=message.from_user.id)
    if check:
        await message.answer('''Это Telegram-bot для рассылки расписания 5 школы г.Лысково!
Напиши в каком ты классе...''')
        await state.set_state(user_states.set_grade)
    elif not check:
        await send_main_menu(message, 'Ты уже подписан на уведомления\nТебе незачем эта команда!')

@dp.message(user_states.set_grade)
async def yes_or_no_grade(message: Message, state: FSMContext):
    all_classes = classOfGetRasp.return_all_classes()
    grade = message.text.replace(" ", "").lower()

    try:
        grade = int(grade)
    except:
        None

    if grade in all_classes:
        await state.clear()
        rasp = classOfGetRasp.return_rasp_for_user(grade=grade)
        requestsInBD.add_user(user_id=message.from_user.id, grade=grade, message=message)
        await send_main_menu(message, f'''Ты подписался на рассылку расписания {grade} класса!
<b>Нажми в меню бота на /info, чтобы узнать, как пользоваться ботом!</b>\n\n{rasp}''')

    elif grade not in all_classes:
        await message.answer(f'Класса {grade} не существует...\nНапиши класс в котором ты обучаешься!')

################# отмена ####################

@dp.message(F.text == 'Отмена')
async def otmena(message: Message, state: FSMContext):
    await state.clear()
    grade = requestsInBD.return_user_grade(user_id=message.from_user.id)

    if grade:
        await send_main_menu(message, classOfGetRasp.return_rasp_for_user(grade=grade))
    
    elif not grade:
        print(f'проблема с {message.from_user.id} {message.from_user.username} отмена')

################# states ####################    

###### прислать другой класс

@dp.message(user_states.other_class)
async def answer_class(message: Message, state: FSMContext):
    await state.clear()
    
    all_classes = classOfGetRasp.return_all_classes()

    grade = message.text
    grade = grade.replace(" ", "").lower() if grade != None else None

    try:
        grade = int(grade)
    except:
        None

    if grade in all_classes:
        rasp = classOfGetRasp.return_rasp_for_user(grade=grade)
        await send_main_menu(message, rasp)
        
    else:
        await send_main_menu(message, 'Такого класса не существует!')

###### изменить класс

@dp.message(user_states.new_class)
async def end_of_new_class(message: Message, state: FSMContext):
    await state.clear()

    all_classes = classOfGetRasp.return_all_classes()

    new_grade = message.text
    new_grade = new_grade.replace(" ", "").lower() if new_grade != None else None

    try:
        new_grade = int(new_grade)
    except:
        None

    if new_grade in all_classes:
        requestsInBD.new_grade(user_id=message.from_user.id, grade=new_grade)
        rasp = classOfGetRasp.return_rasp_for_user(grade=new_grade)
        await send_main_menu(message, f'Вы подписались на рассылку об изменение расписания {new_grade} класса!\n\n{rasp}')

    elif new_grade not in all_classes:
        await send_main_menu(message, f'Такого класса не существует!')

################# Прислать расписание другого класса ####################

@dp.message(F.text == 'Прислать расписание другого класса')
async def other_class(message: Message, state: FSMContext):
    await message.answer('Напишите в чат класс, расписание которого ты хочешь узнать!', reply_markup=otmena_markup)
    await state.set_state(user_states.other_class)

################# Прислать расписание моего класса ####################

@dp.message(F.text == 'Прислать расписание моего класса')
async def my_class(message: Message):
    grade_user = requestsInBD.return_user_grade(user_id=message.from_user.id)
    if grade_user:
        rasp_user = classOfGetRasp.return_rasp_for_user(grade=grade_user)

        await send_main_menu(message, rasp_user)
    
    # elif not grade_user:
    #     print(f'проблема с {message.from_user.id} {message.from_user.username} прислать расп моего класса')

################# Изменить класс ####################

@dp.message(F.text == 'Изменить класс')
async def replace_grade(message: Message, state: FSMContext):
    await message.answer('Пришли новый класс в чат!', reply_markup=otmena_markup)
    await state.set_state(user_states.new_class)

################# подписка/отписка ####################

@dp.message(F.text == 'Отписаться от уведомлений')
async def unsub_notif(message: Message):
    notif_now = requestsInBD.get_notif(message.from_user.id)
    if notif_now == 1:
        requestsInBD.change_notif(user_id=message.from_user.id, value=2)
        await send_main_menu(message=message, text='Вы отписались от уведомлений!\nУдачи!')
    # elif not notif_now:
    #     print(f'проблема с {message.from_user.id} отписаться на уведы')

@dp.message(F.text == 'Подписаться на уведомления')
async def unsub_notif(message: Message):
    notif_now = requestsInBD.get_notif(message.from_user.id)
    if notif_now == 2:
        requestsInBD.change_notif(user_id=message.from_user.id, value=1)
        grade_user = requestsInBD.return_user_grade(user_id=message.from_user.id)

        if grade_user:
            rasp = classOfGetRasp.return_rasp_for_user(grade=grade_user)
            await send_main_menu(message=message, text=f'Вы подписались на уведомаления!\n{rasp}')

    #     elif not grade_user:
    #         print(f'проблема с {message.from_user.id} {message.from_user.username} подписаться на уведы 1 (получить класс)')

    # elif not notif_now:
    #     print(f'проблема с {message.from_user.id} {message.from_user.username} подписаться на уведы 2 (получить нотиф)')

########################### анон сообщение мне #########################################

@dp.message(Command('mes_for_adm'))
async def mes_for_admFunc0(message: Message, state: FSMContext):
    await message.answer('<strong>Напишите, что хотитет передать разработчику</strong> (<i>это может быть рекомендации по улучшению, сообщение об ошибках</i>)!', reply_markup=otmena_markup)
    await state.set_state(user_states.anon_mes)

@dp.message(user_states.anon_mes)
async def mes_for_admFunc0(message: Message, state: FSMContext):
    if message.content_type == ContentType.TEXT:
        mes = str(message.text)
        main_menu = return_main_markup(message.from_user.id)
        await message.answer('<strong>Сообщение отправлено!</strong>', reply_markup=main_menu)
        await bot.send_message(chat_id=1879752333, text=f'<strong>{mes}</strong> - <i>{message.from_user.id}</i>')
        await state.clear()
        with open('anon.txt', 'a', encoding='utf-8') as file:
            file.write(f'({message.from_user.id}, {message.from_user.username}, {message.from_user.first_name}) - {mes}\n')

    else:
        await message.answer('<i>Введите текст!</i>')

############################# отправить сооьщение юзеру по айди ########################################

@dp.message(Command('tell_user'))
async def answerUser(message: Message):
    if message.from_user.id == 1879752333:
        mes = message.text.split()
        try:
            user_id = int(mes[1])
        except:
            await message.answer('<i>Вы не так ввели команду!</i>')
            return
        
        text = ''
        for i in mes[2:]:
            text += i + ' '
        
        try:
            await bot.send_message(chat_id=user_id, text=f'<strong>{text}</strong> - <i>ответ разработчика</i>')
            await message.answer('<i>Текст отправлен!</i>')
        except:
            await message.answer('<i>Юзер заблочил бота!</i>')

    else:
        await message.answer('<i>У тебя недостаточно прав для этой команды!</i>')

######################################### /tell_eve #######################################

@dp.message(Command('tell_eve'))
async def message(message: Message, bot: Bot):
    some_words = message.text[10:]
    if message.from_user.id == 1879752333:
        users = requestsInBD.get_users()
        i = 0
        for user_id in users:
            try:
                await asyncio.sleep(0.1)
                await bot.send_message(chat_id=user_id[0], text=f'<i>{some_words}</i>')
                i += 1
            except:
                print(user_id, 'заблокировал tell_eve')

        await bot.send_message(chat_id=1879752333, text=f'отправлено людям: {i}')
    else:
        await message.answer('<i>У тебя недостаточно прав для этой команды!</i>')

################################# получить количество юзеров ##############################################

@dp.message(Command('get_users_quan'))
async def message(message: Message, bot: Bot):
    if message.from_user.id == 1879752333:
        users = requestsInBD.get_users()
        await message.answer(f'{len(users)} - количество зарегистрированных пользователей')

    else:
        await message.answer('<i>У тебя недостаточно прав для этой команды!</i>')

############################################ опрос работы бота #################################################

@dp.message(Command('work_opros'))
async def funcStartOpros(message: Message, bot: Bot):
    if message.from_user.id == 1879752333:
        users = requestsInBD.get_users()
        i = 0
        for item in users:
            if item[2] == 1:
                await asyncio.sleep(0.1)
                try:
                    await bot.send_message(chat_id=item[0], text='''<i>Всем привет, после разбора некоторых ошибок возник вопрос, а расписание вообще рассылается?
Просьба ответить ниже, присылается ли у вас расписание?</i>''', reply_markup=markup_of_opros)
                    i += 1
                except:
                    print(f'{item} заблокировал work_opros')
        await bot.send_message(chat_id=1879752333, text=f'отправлено людям: {i}')
               
    else:
        await message.answer('У тебя недостаточно прав для этой команды!')

@dp.callback_query(F.data.in_(yes_or_no_dict.keys()))
async def funcEndOpros(callback: CallbackQuery):
    yes_or_no = yes_or_no_dict[callback.data]
    with open('answers.txt', 'a', encoding='utf-8') as file:
        file.write(f'{yes_or_no} ({callback.from_user.id}, {callback.from_user.first_name}, {callback.from_user.username})\n')

    try:
        await bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id, text='<i>Благодарю за ответ!</i>', reply_markup=None)

    except:
        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
        await bot.send_message(chat_id=callback.from_user.id, text='<i>Благодарю за ответ!</i>')

#################################### /kill #################################

@dp.message(Command('kill'))
async def funcKillPO(message: Message):
    sys.exit()

###################################### /info ################################################

@dp.message(Command('info'))
async def info(message: Message):
    await message.answer('''<b>•</b> Ты уже подписан на уведомления. Чтобы отписаться от них, 
нажми <b>"Отписаться от уведомлений"</b>.
<b>•</b> Чтобы узнать свое расписание, нажми на <b>"Прислать расписание моего класса"</b>.
<b>•</b> Если ты хочешь узнать расписание другого класса, но не изменять свой, нажми на 
<b>"Прислать расписание другого класса"</b>.
<b>•</b> Если ты хочешь изменить свой класс обучения, нажми <b>"Изменить класс"</b>.
<b>В целом все, будут вопросы, задавайте</b> @xqwerty69
''')

####################################### тригер на изменение ##########################################3

async def check_of_rasp():
    while True:
        await asyncio.sleep(120)

        async def func_of_mailing(new_id):
            if new_id != "":
                
                down_true_false = classOfGetRasp.download_rasp('расписание')
                users = requestsInBD.get_users()

                if down_true_false:
                    classOfGetRasp.write_all_classes()

                i = 0

                for user in users:
                    if user[2] == 1:
                        if down_true_false:
                            rasp = classOfGetRasp.return_rasp_for_user(user[1])
                            text = rasp

                        elif not down_true_false:
                            text = r'Расписание на завтра уже на сайте!\nЗаходи и смотри каких уроков нет...\n\n<a href="https://sites.google.com/view/perspectiva99/%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F-%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0">Ссылка на расписание</a>'

                        try:
                            await asyncio.sleep(0.1)
                            await bot.send_message(chat_id = user[0], text=text)
                            i += 1
                        except:
                            print(user, 'заблокировал рассылка расписания')    

                await bot.send_message(chat_id=1879752333, text=f'разослано людям: {i}')


        new_id = classOfGetRasp.id_file_of_rasp()
        last_id = open('last_id_file.txt', encoding='utf-8').read()
        check_fl = await classOfGetRasp.check_files()
        

        if (last_id != new_id and new_id != False):
            with open('last_id_file.txt', 'w', encoding='utf-8') as file:
                file.write(new_id)
                file.close()
            await func_of_mailing(new_id)

        elif check_fl:
            await func_of_mailing(new_id)

async def dp_polling():
    await dp.start_polling(bot, polling_timeout=2)

async def main():
    task1 = asyncio.create_task(check_of_rasp())
    task2 = asyncio.create_task(dp_polling())
    await task1
    await task2

if __name__ == '__main__':
    asyncio.run(main()) 
