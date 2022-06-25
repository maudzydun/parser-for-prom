import requests
import random
from time import sleep
from bs4 import BeautifulSoup as bs4
import sqlite3  as sql



# эта функция принимает один параметр - ссылку на карточку товара на пром юа и записывает в БД another_site.sqlite данные в 2 таблицы 
def card_parser(card_href, url_site, group_title):
    headers = {"user-agent": "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.188 Safari/537.36 CrKey/1.54.250320"}
    response = requests.get(card_href, headers=headers)
    sleep(random.randint(1, 5))
    soup = bs4(response.text, 'html.parser') # Получили весь код страницы с товаром и ее распарсили

    id = soup.find('span', {'data-qaid': 'product_code'}).text  # получили код товара            
    name = soup.find('span', {'data-qaid': 'product_name'}).text  # Название товара            
    v_nalicii = soup.find('li', {'data-qaid': 'presence_data'}).text  # наличие
    # цена
    try:
        price = soup.find('span', {'data-qaid': 'product_price'}).text +" "+ soup.find('span', {'data-qaid': 'currency'}).text
    except AttributeError:
        price = soup.find('p', {'data-qaid': 'product_price'}).text 
    else:
        price = None
    # ===============
    description = soup.find('div', {'data-qaid': 'product_description'}).get_text()  # описание (весь текст из блока)
    # ===============
    specifications_soup = soup.find_all('td', {'class': 'b-product-info__cell'}) #суп из характеристик
    # дальше этот список нам нужно преобразовать , перебрать и опять преобразовать в понятный формат
    spisok = []  # создаем список в котором мы сохраним значения характеристик 
    for i in specifications_soup:
        spisok.append((i.getText()).strip())
        # перебираем наши характеристики и обрезаем лишние пробелы и абзацы по обе стороны и добавляем все в список
        # записываем переменную характеристикики списком
    specifications = []
    for el in range(1, len(spisok) + 1,2):  # берем наш список характеристик и перебираем его с помощи ренжа с шагом через один
        specification = [spisok[el - 1], spisok[el]]  # записываем характеристику и значение в тупл
        specifications.append(specification)  # и добавляем его в список характеристики

    
    connection = sql.connect(f'{url_site}.sqlite') #создаем или конектимся с базой данных (ее название может быть с расширением db или sqlite)
    curs = connection.cursor() #c помощью курсора можно совршать действия связаные с базой данных которая находится в переменной конекшн

    # в табличку товары вносим айди, имя, наличие, цену и описание с помощью переменных
    descriptions_with_parametrs = (f'''INSERT INTO {group_title} (id, name, v_nalicii, price, description) VALUES(?, ?, ?, ?, ?);''')
    description_tuple = (id, name, v_nalicii, price, description)
    curs.execute(descriptions_with_parametrs, description_tuple)
    connection.commit()

    # в табличку характеристики вносим айди (чтобы можно было потом привязать к какому товару идут эти характеристики), название характеристики и ее значение 
    for speci, meaning in specifications:
        specifications_with_parametrs = (f'''INSERT INTO {group_title}_specifications (id, specification, value) VALUES(?, ?, ?);''')
        specifications_tuple = (id, speci, meaning)
        curs.execute(specifications_with_parametrs, specifications_tuple)
        connection.commit()


# эта функция принимает ссылку на группу товаров на сайте и возвращает число - количество страниц по ссылке
def how_many_pages(href):
    headers = {"user-agent": "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.188 Safari/537.36 CrKey/1.54.250320"}
    response = requests.get(href, headers=headers)
    sleep(random.randint(1, 5))
    soup = bs4(response.text, 'html.parser') #Получаем суп из полученых категорий ссылки
    # находим значение последней страницы 
    try:
        count_page = int(soup.find('span', {'class':'b-pager__dotted-link'}).find_next_sibling().text)
        # Если на странице больше 3х страниц тогда берем значение последней страницы из блок после 3х точек
    except:
        try:
            count_page = int(soup.find('div', {'class':'b-pager'}).find('a', {'class':'b-pager__link b-pager__link_pos_last'}).find_previous_sibling().text) #если 2 или 3 страницы - берем последнее значение в блоке див
        except:
            count_page = 1 #если одна - выдает ошибку , поэтому просто записываем 1 
    return count_page


