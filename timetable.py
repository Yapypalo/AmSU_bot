# Импортируем необходимые модули для работы с Selenium и BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import bs4

# Словарь для преобразования номера дня недели в его название
weeks_days = {1: 'Понедельник', 2: 'Вторник', 3: 'Среда', 4: 'Четверг', 5: 'Пятница', 6: 'Суббота', 7: 'Воскресенье'}

# Функция для получения списка групп с сайта АмГУ
def get_groups():
    # Создаем экземпляр драйвера Chrome
    driver = webdriver.Chrome()
    # Открываем страницу с расписанием групп
    driver.get("https://www.amursu.ru/obrazovanie/timetable/timetable-group/")
    
    # Находим все ссылки, содержащие функцию "appendGroupTimetable" в атрибуте onclick
    all_links = driver.find_elements(By.XPATH, '//a[contains(@onclick, "appendGroupTimetable")]')
    
    # Создаем списки для хранения ключей (ID групп) и значений (названий групп)
    links_keys = []
    links_values = []
    
    # Проходим по всем найденным ссылкам
    for link in all_links:
        # Извлекаем ID группы из атрибута onclick
        links_keys.append(str.removesuffix(
            str.removeprefix(link.get_attribute("onclick"), 'appendGroupTimetable('), ')'
        ))
        # Извлекаем текстовое название группы
        links_values.append(link.text)
    
    # Создаем словарь, где ключи — это ID групп, а значения — названия групп
    links = dict(zip(links_keys, links_values))
    
    # Закрываем браузер
    driver.quit()
    
    # Возвращаем словарь с группами
    return links


# Функция для получения списка занятий из строки таблицы
def get_timetable_list(row):
    output = []
    
    # Добавляем время занятия (первый столбец)
    output.append(row.find('td').text)
    
    # Обрабатываем третий и четвертый столбцы (информацию о занятиях)
    thrd_column = row.find_all('td')[2:]
    if len(thrd_column) == 2:
        fore_column = thrd_column[1]
        thrd_column = thrd_column[0]
        fore_column_list = [['нет разделения']]
    else:
        fore_column = []
        fore_column_list = [['нет разделения']]
        thrd_column = thrd_column[0]
    
    # Создаем список для хранения информации о занятиях в третьем столбце
    thrd_column_list = []
    listOfweeks = thrd_column.find_all('div', class_="ui top left attached label blue")
    listOfheaders = thrd_column.find_all('div', class_='ui header small')
    listOfLocations = thrd_column.find_all('div', class_='ui label image')
    listOfLectures = thrd_column.find_all('div', class_='ui label grey image')
    
    if listOfLocations:
        for i in range(len(listOfheaders)):
            a = []
            if listOfweeks:
                a.append(listOfweeks[i].text)  # Номер недели
            a.append(listOfheaders[i].find('strong').text)  # Название предмета
            if listOfheaders[i].find('div', class_='sub header'):
                a.append(listOfheaders[i].find('div', class_='sub header').text)  # Подробности
            a.append(listOfLocations[i].text)  # Аудитория
            a.append(listOfLectures[i].text)  # Преподаватель
            thrd_column_list.append(a)
    else:
        thrd_column_list = [['Занятий нет']]  # Если занятий нет
    
    # Обрабатываем четвертый столбец (если он существует)
    if fore_column_list == []:
        fore_column_list = []
        listOfweeks = fore_column.find_all('div', class_="ui top left attached label blue")
        listOfheaders = fore_column.find_all('div', class_='ui header small')
        listOfLocations = fore_column.find_all('div', class_='ui label image')
        listOfLectures = fore_column.find_all('div', class_='ui label grey image')
        
        if listOfLocations:
            for i in range(len(listOfheaders)):
                a = []
                if listOfweeks:
                    a.append(listOfweeks[i].text)  # Номер недели
                a.append(listOfheaders[i].find('strong').text)  # Название предмета
                if listOfheaders[i].find('div', class_='sub header'):
                    a.append(listOfheaders[i].find('div', class_='sub header').text)  # Подробности
                a.append(listOfLocations[i].text)  # Аудитория
                a.append(listOfLectures[i].text)  # Преподаватель
                fore_column_list.append(a)
    
    # Добавляем информацию о занятиях в выходной список
    output.append([thrd_column_list, fore_column_list])
    
    return output


# Функция для получения расписания для конкретной группы
def get_table(key, group):
    output = {}
    
    # Создаем экземпляр драйвера Chrome
    driver = webdriver.Chrome()
    # Открываем страницу с расписанием для указанной группы
    driver.get("https://www.amursu.ru/obrazovanie/timetable/timetable-group/?id_group=" + str(key))
    driver.set_page_load_timeout(10)  # Устанавливаем таймаут загрузки страницы
    
    # Находим все таблицы на странице
    data = driver.find_elements(By.TAG_NAME, 'table')
    
    rows = []
    # Извлекаем HTML-код каждой таблицы
    for i in data:
        rows.append(i.get_attribute('innerHTML'))
    
    day = 0  # Счетчик дней недели
    
    # Проходим по всем таблицам
    for i in rows:
        a = []
        soup = bs4.BeautifulSoup(i, 'html.parser')  # Парсим HTML с помощью BeautifulSoup
        day_list = soup.find_all('tr')[1:]  # Находим все строки таблицы (пропускаем заголовок)
        day += 1
        
        # Обрабатываем каждую строку таблицы
        for j in day_list:
            a.append(get_timetable_list(j))
        
        # Добавляем расписание для текущего дня в выходной словарь
        output[weeks_days[day]] = a
    
    # Закрываем браузер
    driver.quit()
    
    return output