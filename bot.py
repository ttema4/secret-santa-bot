import telebot
import config
import sqlite3

bot = telebot.TeleBot(config.TOKEN)
conn = sqlite3.connect("SecretSanta.db", check_same_thread=False)
cursor = conn.cursor()
new_user = {}


@bot.message_handler(commands=['start'])
def start_command(message):
    if message.chat.id != config.MY_ID:
        if (message.chat.id,) not in cursor.execute("SELECT id FROM main").fetchall():
            new_user[message.chat.id] = {'sex': '',
                                         'name_sur': '',
                                         'class': '',
                                         'wishes': '',
                                         'would_sex': ''}
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(
                telebot.types.InlineKeyboardButton(
                    'Написать разработчику👨🏻‍💻', url='telegram.me/ttema4'
                )
            )
            bot.send_message(
                message.chat.id,
                'Привет👋🏻 Это тайный санта!\n\n'
                'Если готов учавствовать,\n'
                'просто отвечай на вопросы\n\n'
                'Поддержка ⤵️', reply_markup=keyboard
            )
            keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            buttons = ["Я мальчик 🧑🏻", "Я девочка 👩🏻"]
            keyboard2.add(*buttons)
            bot.send_message(
                message.chat.id,
                'Для начала выберите свой пол', reply_markup=keyboard2
            )
            bot.register_next_step_handler(message, get_sex)
        else:
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(
                telebot.types.InlineKeyboardButton(
                    'Написать разработчику👨🏻‍💻', url='telegram.me/ttema4'
                )
            )
            bot.send_message(message.from_user.id, 'Вы в игре! Ожидайте новостей!\n'
                                                   'Вопросы? Пиши в поддержку ⤵️', reply_markup=keyboard)
            bot.register_next_step_handler(message, wait_news)
    else:
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(
            telebot.types.InlineKeyboardButton(
                'Заявки', callback_data='admin-apl')
        )
        keyboard.add(
            telebot.types.InlineKeyboardButton(
                'Рассылка', callback_data='admin-malling')
        )
        keyboard.add(
            telebot.types.InlineKeyboardButton(
                'Статистика', callback_data='admin-statistic')
        )
        keyboard.add(
            telebot.types.InlineKeyboardButton(
                'Начать игру', callback_data='admin-start_game')
        )
        bot.send_message(message.chat.id, '⚙️ ADMIN MENU ⚙️', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data.startswith('admin-'):
        if call.data == 'admin-apl':
            if not len(cursor.execute("SELECT * FROM main").fetchall()):
                bot.send_message(call.message.chat.id, 'Новых заявок нет!',
                                 reply_markup=telebot.types.ReplyKeyboardRemove())
                start_command(call.message)
            else:
                el = cursor.execute("SELECT * FROM main").fetchone()
                keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                buttons = ["Одобрить ✅", "Удалить ❌"]
                keyboard.add(*buttons)
                bot.send_message(call.message.chat.id, f'🔹Ссылка: tg://user?id={el[0]}\n'
                                                       f'🔹id: {el[0]}\n'
                                                       f'🔹Пол: {el[1]}\n'
                                                       f'🔹Имя: {el[2]}\n'
                                                       f'🔹Класс: {el[3]}\n'
                                                       f'🔹Пожелания: {el[4]}\n'
                                                       f'🔹Кому: {el[5]}\n\n'
                                                       f'Осталось: {len(cursor.execute("SELECT * FROM main").fetchall())}',
                                 reply_markup=keyboard)
                bot.register_next_step_handler(call.message, check_apl)
        elif call.data == 'admin-malling':
            malling(call.message)
        elif call.data == 'admin-statistic':
            statistic(call.message)
        elif call.data == 'admin-start_game':
            bot.send_message(call.message.chat.id, 'Вы уверены?\n'
                                                   'Для подтверждения отправьте "yes"')
            bot.register_next_step_handler(call.message, start_game)


def start_game(message):
    if message.text == 'yes':
        peop = cursor.execute("SELECT * FROM final").fetchall()
        last = rec_search(message, 0, peop.copy())
        print(last[2], '->', peop[0][2])
        bot.send_message(last[0], f'🎉 Игра началась!\n'
                                  f'Тебе попался {peop[0][2]}.\n'
                                  f'Он учится в {peop[0][3]}. К слову, он оставил пожелания: {peop[0][4]}.\n'
                                  f'Да начнётся игра! 🎉')
        bot.send_message(message.chat.id, 'Игра началась!')
    start_command(message)


def rec_search(message, id, peoples):
    if len(peoples) == 1:
        return peoples[0]
    for n_id, el in enumerate(peoples):
        if n_id != id and peoples[id][5].split('-')[1] == peoples[n_id][1].split('-')[1]:
            print(peoples[id][2], '->', peoples[n_id][2])
            a = peoples[n_id]
            del (peoples[id])
            n_id = peoples.index(a)
            return rec_search(message, n_id, peoples)
    else:
        for n_id, el in enumerate(peoples):
            if n_id != id:
                print(peoples[id][2], '->', peoples[n_id][2])
                bot.send_message(peoples[id][0], f'Игра началась!\n'
                                                 f'Итак, ты даришь подарки человеку, '
                                                 f'которого зовут {peoples[n_id][2]}.\n'
                                                 f'Он учится в {peoples[n_id][3]}. К слову, '
                                                 f'он оставил пожелания: {peoples[n_id][4]}.\n'
                                                 f'Да начнётся игра!')
                a = peoples[n_id]
                del (peoples[id])
                n_id = peoples.index(a)
                return rec_search(message, n_id, peoples)


def statistic(message):
    bot.send_message(message.chat.id, f'🔹Участников: {len(cursor.execute("SELECT * FROM final").fetchall())}\n'
                                      f'🔹Заявок: {len(cursor.execute("SELECT * FROM main").fetchall())}\n')
    start_command(message)


def malling(message):
    bot.send_message(message.chat.id, 'Введите текст для рассылки:')
    bot.register_next_step_handler(message, send_malling)


def send_malling(message):
    for el in cursor.execute("SELECT id FROM main").fetchall():
        bot.send_message(el[0], message.text)

    for el in cursor.execute("SELECT id FROM final").fetchall():
        bot.send_message(el[0], message.text)

    start_command(message)


def check_apl(message):
    el = cursor.execute("SELECT * FROM main").fetchone()
    if message.text.startswith('О'):
        cursor.execute("INSERT INTO final VALUES (?, ?, ?, ?, ?, ?)", tuple(el))
        conn.commit()
        bot.send_message(str(el[0]), 'Ваша заявка одобрена! ✅')
    else:
        bot.send_message(str(el[0]), 'Ваша была анулирована =(\n'
                                     'Создайте новую при помощи /start')
    cursor.execute("DELETE FROM main WHERE id = ?", (el[0],))
    conn.commit()
    if len(cursor.execute("SELECT * FROM main").fetchall()):
        el = cursor.execute("SELECT * FROM main").fetchone()
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Одобрить ✅", "Удалить ❌"]
        keyboard.add(*buttons)
        bot.send_message(message.chat.id, f'🔹Ссылка: tg://user?id={el[0]}\n'
                                          f'🔹id: {el[0]}\n'
                                          f'🔹Пол: {el[1]}\n'
                                          f'🔹Имя: {el[2]}\n'
                                          f'🔹Класс: {el[3]}\n'
                                          f'🔹Пожелания: {el[4]}\n'
                                          f'🔹Кому: {el[5]}\n\n'
                                          f'Осталось: {len(cursor.execute("SELECT * FROM main").fetchall())}',
                         reply_markup=keyboard)
        bot.register_next_step_handler(message, check_apl)
    else:
        bot.send_message(message.chat.id, 'Больше заявок нет!', reply_markup=telebot.types.ReplyKeyboardRemove())
        start_command(message)


def get_sex(message):
    global new_user
    if message.text in ["Я мальчик 🧑🏻", "Я девочка 👩🏻"]:
        if message.text.startswith('Я мал'):
            new_user[message.chat.id]['sex'] = 'sex-man'
        else:
            new_user[message.chat.id]['sex'] = 'sex-girl'
        bot.send_message(
            message.chat.id,
            'Как вас зовут?\n'
            '❕ Пример: "Иван Иванов"')
        bot.register_next_step_handler(message, get_name)
    else:
        keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ["Я мальчик 🧑🏻", "Я девочка 👩🏻"]
        keyboard2.add(*buttons)
        bot.send_message(
            message.chat.id,
            '❌ Выберите вариант с клавиатуры\n\n'
            'Для начала выберите свой пол', reply_markup=keyboard2
        )
        bot.register_next_step_handler(message, get_sex)


def get_name(message):
    global new_user
    if len(message.text.split()) != 2:
        bot.send_message(
            message.chat.id,
            '❌ Пишите настоящие имена и фамилию\n\n'
            'Как вас зовут?\n'
            '❕ Пример: "Иван Иванов"'
        )
        bot.register_next_step_handler(message, get_name)
    else:
        new_user[message.chat.id]['name_sur'] = message.text.capitalize()
        bot.send_message(message.from_user.id, 'В каком вы классе?\n'
                                               '❕ Пример: "10а"')
        bot.register_next_step_handler(message, get_class)


def get_class(message):
    global new_user
    if not message.text[-1].isalpha() or not message.text[:-1].isdigit():
        bot.send_message(message.from_user.id, '❌ Пишите свой настоящий класс\n\n'
                                               'В каком вы классе?\n'
                                               '❕ Пример: "10а"')
        bot.register_next_step_handler(message, get_class)
    else:
        new_user[message.chat.id]['class'] = message.text.capitalize()
        bot.send_message(message.from_user.id, 'Напишите пожелания подарков, которые будут дарить вам\n'
                                               '❕ Если у вас на что-то аллергия стоит также написать')
        bot.register_next_step_handler(message, get_wishes)


def get_wishes(message):
    global new_user
    new_user[message.chat.id]['wishes'] = message.text
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ["Мальчику 🧑🏻", "Девочке 👩🏻"]
    keyboard.add(*buttons)
    bot.send_message(message.from_user.id, 'Кому вы хотели бы дарить?\n'
                                           'Система учтёт ваши пожелания', reply_markup=keyboard)
    bot.register_next_step_handler(message, get_would_sex)


def get_would_sex(message):
    global new_user
    if message.text in ["Мальчику 🧑🏻", "Девочке 👩🏻"]:
        if message.text.startswith('Мал'):
            new_user[message.chat.id]['would_sex'] = 'would-man'
        else:
            new_user[message.chat.id]['would_sex'] = 'would-girl'
        write_new_user(message)
    else:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ["Мальчику 🧑🏻", "Девочке 👩🏻"]
        keyboard.add(*buttons)
        bot.send_message(message.from_user.id, '❌ Выберите вариант с клавиатуры\n\n'
                                               'Кому вы хотели бы дарить?\n'
                                               '(Мы не гарантируем, но учтем ваши пожелания)', reply_markup=keyboard)
        bot.register_next_step_handler(message, get_would_sex)


def write_new_user(message):
    cursor.execute("INSERT INTO main VALUES (?, ?, ?, ?, ?, ?)",
                   [message.chat.id] + list(new_user[message.chat.id].values()))
    conn.commit()
    bot.send_message(message.chat.id, 'Ваша заявка на участие успешно создана! ✅')
    bot.send_message(config.MY_ID, '❗️У вас +1 новая заявка!')
    bot.register_next_step_handler(message, wait_news)


@bot.message_handler()
def wait_news(message):
    if (message.chat.id,) not in cursor.execute("SELECT id FROM main").fetchall():
        start_command(message)
    else:
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(
            telebot.types.InlineKeyboardButton(
                'Написать разработчику👨🏻‍💻', url='telegram.me/ttema4'
            )
        )
        bot.send_message(message.from_user.id, 'Вы в игре! Ожидайте новостей!\n'
                                               'Вопросы? Пиши в поддержку ⤵️', reply_markup=keyboard)
        bot.register_next_step_handler(message, wait_news)


bot.polling(none_stop=True)
