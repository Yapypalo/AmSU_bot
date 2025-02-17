# Импортируем необходимые модули для работы с SQLite и получения расписания
import sqlite3
import timetable

# Словарь для преобразования номера дня недели в его название
weeks_days = {1: 'Понедельник', 2: 'Вторник', 3: 'Среда', 4: 'Четверг', 5: 'Пятница', 6: 'Суббота', 7: 'Воскресенье'}

# Функция для создания таблицы в базе данных и заполнения ее данными о расписании
def create_table(key, group):
    # Подключаемся к базе данных AmGU_timetableDB.db
    connection = sqlite3.connect('AmGU_timetableDB.db')
    cursor = connection.cursor()

    # Создаем таблицу для указанной группы, если она еще не существует
    cursor.execute('''CREATE TABLE IF NOT EXISTS "''' + group + '''" (weekday TEXT, time TEXT, subject TEXT, 
                subject_type TEXT, location TEXT, lectore TEXT, week TEXT, subgroup INTEGER)''')

    # Получаем расписание для указанной группы
    data = timetable.get_table(key, group)

    # Проходим по всем дням недели (от 1 до 7)
    for i in range(1, 8):
        # Получаем название дня недели
        weekday = weeks_days[i]

        # Проходим по каждой строке расписания для текущего дня
        for row in data[weekday]:
            time = row[0]  # Время занятия
            subgroup = 1  # Начинаем с первой подгруппы

            # Обрабатываем данные для каждой подгруппы
            for subgroup_iter in row[1]:
                for subject_iter in subgroup_iter:
                    week = None
                    subject = None
                    subject_type = None
                    location = None
                    lectore = None

                    # Пропускаем записи, где нет разделения на подгруппы
                    if subject_iter[0] == 'нет разделения':
                        continue

                    # Обрабатываем случай, когда занятий нет
                    if subject_iter[0] == 'Занятий нет':
                        subject = 'Занятий нет'
                    else:
                        # Определяем неделю, если она указана
                        if subject_iter[0] in ['1 неделя.', '2 неделя.']:
                            week = subject_iter[0]
                            subject = subject_iter[1]
                        else:
                            subject = subject_iter[0]

                        # Определяем тип занятия, аудиторию и преподавателя
                        if (subject_iter[1] == 'лекция') or ('до ' in subject_iter[1]):
                            subject_type = subject_iter[1]
                            location = subject_iter[2]
                            lectore = subject_iter[3]
                        elif (subject_iter[2] == 'лекция') or ('до ' in subject_iter[2]):
                            subject_type = subject_iter[2]
                            location = subject_iter[3]
                            lectore = subject_iter[4]
                        else:
                            if subject_iter[0] in ['1 неделя.', '2 неделя.']:
                                location = subject_iter[2]
                                lectore = subject_iter[3]
                            else:
                                location = subject_iter[1]
                                lectore = subject_iter[2]

                    # Вставляем данные в таблицу
                    cursor.execute('''INSERT INTO "''' + group + '''" VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                                   (weekday, time, subject, subject_type, location, lectore, week, subgroup))
                    print(weekday, ' ', time, ' ', subject, ' ', subject_type, ' ', location, ' ', lectore, ' ', week, ' ', subgroup)

                # Переходим ко второй подгруппе
                subgroup = 2

        print()  # Пустая строка для разделения дней недели

    # Сохраняем изменения в базе данных
    connection.commit()
    # Закрываем соединение с базой данных
    connection.close()


# Вызываем функцию для создания таблицы и заполнения ее данными
create_table(1749, "0109-об")