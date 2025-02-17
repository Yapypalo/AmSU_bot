import sqlite3
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

def DaySchedule(group, weekday):
    """
    Получает расписание для указанной группы на указанный день недели.

    group: Название группы (строка)
    weekday: День недели (строка)
    return: Словарь с расписанием
    """
    try:
        # Подключаемся к базе данных с использованием контекстного менеджера
        with sqlite3.connect('AmGU_timetableDB.db') as conn:
            cursor = conn.cursor()

            # Выполняем запрос для получения расписания
            query = f'SELECT * FROM "{group}" WHERE weekday = ?'
            cursor.execute(query, (weekday,))
            output = cursor.fetchall()

        # Создаем словарь для хранения расписания
        schedule_dict = {}

        # Проходим по каждой записи в результате запроса
        for entry in output:
            day = entry[0]
            time = entry[1]
            subgroup = entry[7]
            week = entry[6]
            subject = entry[2]
            description = entry[3]
            room = entry[4]
            teacher = entry[5]

            # Заполняем словарь расписания
            schedule_dict.setdefault(day, {}).setdefault(time, {}).setdefault(subgroup, {}).setdefault(week, {})
            schedule_dict[day][time][subgroup][week] = {
                'название предмета': subject,
                'подробности': description,
                'аудитория': room,
                'преподаватель': teacher
            }

        logging.info(f"Получено расписание для группы {group} на {weekday}")
        return schedule_dict

    except sqlite3.Error as e:
        logging.error(f"Ошибка при получении расписания: {e}")
        return {}  # Возвращаем пустой словарь в случае ошибки