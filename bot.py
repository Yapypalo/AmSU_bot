# Импортируем необходимые модули для работы с Telegram Bot API и SQLite базой данных
import logging
from telegram.constants import ParseMode  # Для форматирования сообщений
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup  # Для создания кнопок и обработки ответов
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler, filters, MessageHandler,
    ConversationHandler, CallbackContext, CallbackQueryHandler
)  # Для создания обработчиков команд и событий
from config import TOKEN  # Импортируем конфигурационные данные (токен бота)
import sqlite3  # Для работы с SQLite базой данных
from DBdownload import DaySchedule  # Модуль для загрузки расписания из базы данных
import datetime  # Для работы с датами и временем
from userRegistration import *

# Определяем состояние для диалога регистрации пользователя
GROUP_NUMBER = range(1)

# Настройка логирования для отслеживания работы бота
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Создаем клавиатуру с кнопками дней недели
keyboard = [
    [InlineKeyboardButton("Пн", callback_data='Понедельник'),
     InlineKeyboardButton("Вт", callback_data='Вторник'),
     InlineKeyboardButton("Ср", callback_data='Среда'),
     InlineKeyboardButton("Чт", callback_data='Четверг'),
     InlineKeyboardButton("Пт", callback_data='Пятница'),
     InlineKeyboardButton("Сб", callback_data='Суббота'),
     ]
]
reply_markup = InlineKeyboardMarkup(keyboard)  # Создаем объект InlineKeyboardMarkup


# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    username = update.message.from_user.first_name  # Получаем имя пользователя
    user_id = update.message.from_user.id  # Получаем ID пользователя

    # Проверяем, существует ли пользователь в базе данных
    if user_exists(user_id):
        await update.message.reply_text(f'Добро пожаловать {username}', reply_markup=reply_markup)
    else:
        # Если пользователь не зарегистрован, предлагаем ввести номер группы
        await update.message.reply_text(f'Привет, {username}! Для продолжения введите номер группы в полнои виде.')
        return GROUP_NUMBER  # Переходим к состоянию ввода номера группы


# Обработчик регистрации пользователя
async def register(update: Update, context: CallbackContext) -> int:
    group_number = update.message.text  # Получаем введенный номер группы

    # Проверяем корректность формата номера группы
    if not is_valid_group_number(group_number):
        await update.message.reply_text('Неправильный формат номера группы. Пожалуйста, введите номер группы снова.')
        return GROUP_NUMBER

    userId = update.message.from_user.id  # Получаем ID пользователя
    username = update.message.from_user.username  # Получаем имя пользователя

    # Проверяем, зарегистрирован ли уже пользователь
    if user_exists(userId):
        await update.message.reply_text(f'Пользователь {username} уже зарегистрирован.', reply_markup=reply_markup)
    else:
        # Регистрируем пользователя в базе данных
        register_user(userId, username, group_number)
        await update.message.reply_text(f'Пользователь {username} успешно зарегистрирован в группе {group_number}.', reply_markup=reply_markup)

    return ConversationHandler.END  # Завершаем диалог


# Обработчик нажатия на кнопки дней недели
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    userId = update.effective_user.id  # Получаем ID пользователя
    username = update.effective_user.first_name  # Получаем имя пользователя
    query = update.callback_query  # Получаем объект запроса
    await query.answer()  # Отвечаем на запрос

    # Подключаемся к базе данных
    conn = sqlite3.connect('AmGU_timetableDB.db')
    cursor = conn.cursor()

    # Получаем группу пользователя из базы данных
    cursor.execute("SELECT usergroup FROM users WHERE userId = ?", (userId,))
    usergroup = cursor.fetchone()

    # Формируем сообщение с расписанием
    message = ''
    print(username)
    print(userId)
    print(usergroup)
    timetable = DaySchedule(usergroup[0], query.data)  # Получаем расписание для выбранного дня

    # Определяем текущую неделю (число недели по ISO)
    week_number = datetime.datetime.today().isocalendar()[1]

    # Добавляем информацию о текущей неделе в сообщение
    if int(week_number) % 2 == 0:
        message += f'Текущая неделя 2 \n'
    if int(week_number) % 2 != 0:
        message += f'Текущая неделя 1 \n'

    # Генерируем текст расписания
    for time in timetable[query.data]:
        message += f'{time}:\n'
        for subgroup in timetable[query.data][time]:
            if len(timetable[query.data][time]) > 1:
                message += f'-{subgroup} подгруппа:\n'
            for week in timetable[query.data][time][subgroup]:
                if week is not None:
                    if (int(week[0]) % 2 == 0) != (int(week_number) % 2 == 0):
                        continue
                    if (int(week[0]) % 2 != 0) != (int(week_number) % 2 != 0):
                        continue
                bold = True
                message += '---'
                for item in timetable[query.data][time][subgroup][week]:
                    if bold:
                        message += '*'
                    if timetable[query.data][time][subgroup][week][item] is None:
                        message += ''
                    else:
                        message += timetable[query.data][time][subgroup][week][item]
                    if bold:
                        message += '*'
                        bold = False
                    message += ' '
                message += '\n'
        message += '\n'

    conn.close()  # Закрываем соединение с базой данных

    # Отправляем сформированное сообщение с расписанием
    await update.effective_message.reply_text(text=message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)


# Обработчик команды /update
async def chat_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Обновление чата', reply_markup=reply_markup)


# Точка входа в программу
if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()  # Создаем экземпляр приложения с указанным токеном

    # Создаем обработчик диалога для регистрации пользователя
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],  # Точка входа — команда /start
        states={
            GROUP_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, register)]  # Состояние ввода номера группы
        },
        fallbacks=[],  # Список фоллбэков (пустой в данном случае)
    )

    # Добавляем обработчики к приложению
    application.add_handler(conv_handler)  # Обработчик диалога регистрации
    application.add_handler(CallbackQueryHandler(button))  # Обработчик нажатий на кнопки
    application.add_handler(CommandHandler('update', chat_update))  # Обработчик команды /update

    # Запускаем бота
    application.run_polling()