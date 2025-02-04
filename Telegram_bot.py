# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 15:43:14 2025

Получение данных с hh.ru по API

@author: irina
"""

import requests
import fake_useragent
from bs4 import BeautifulSoup
from telebot import TeleBot, types
import json
from collections import Counter
import re

# Токен Telegram-бота
TOKEN = "7653647135:AAH2PSRO_6eE3yyrR3opc17PuMybs59KiuE"

# Доступные регионы и уровни опыта
regions = {"Москва": 1, "Санкт-Петербург": 2}
levels = {"Junior": "noExperience", "Middle": "between1And3", "Senior": "moreThan6"}
categories = {"Data Analyst": "Data+Analyst", "Data Scientist": "Data+Scientist", "Data Engineer": "Data+Engineer"}

# Инициализация бота
bot = TeleBot(TOKEN)

# Функция парсера
def parse_vacancies(region_id, level_id, category_text):
    page_number = 0
    hrefs = []  # Список ссылок на вакансии
    salaries = []  # Список зарплат
    companies = []  # Список компаний

    while True:
        url = f'https://hh.ru/search/vacancy?area={region_id}&search_field=name&search_field=company_name&search_field=description&enable_snippets=false&experience={level_id}&text={category_text}&page={page_number}'
        user_ag = fake_useragent.UserAgent()

        try:
            response = requests.get(url, headers={"user-agent": user_ag.random}, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")
        except requests.exceptions.RequestException as e:
            return f"Ошибка при запросе: {e}\n"

        items = soup.find_all("div", class_="magritte-redesign")

        if not items:
            break

        for item in items:
            # Сбор ссылок
            hre = item.find("a").get("href")
            hrefs.append(hre)

            # Сбор зарплат
            salary_tag = item.find("span", class_="magritte-text___pbpft_3-0-26 magritte-text_style-primary___AQ7MW_3-0-26 magritte-text_typography-label-1-regular___pi3R-_3-0-26")
            if salary_tag:
                salary_text = salary_tag.text.replace("\u202f", " ")  # Убираем спецсимволы пробела
                # Извлекаем только цифры
                salary = re.findall(r'\d+', salary_text)
                # Если нашли цифры, добавляем их в список
                if salary:
                    salaries.append(int(salary[0]))  # добавляем число (первое из найденных цифр)

            # Сбор компаний
            company_tag = item.find("a", class_="magritte-link___b4rEM_4-3-21 magritte-link_style_neutral___iqoW0_4-3-21")
            if company_tag:
                companies.append(company_tag.text.strip())

        page_number += 1
        
    # Инициализация списков
    decoded_texts = []
    valid_links = []
    
    # Фильтруем элементы
    for item in hrefs:
        if isinstance(item, str):
            if item.startswith("https://") or item.startswith("http://"):
                valid_links.append(item)  # Это ссылка
            else:
                try:
                    # Пробуем декодировать строку
                    decoded_text = json.loads(f'"{item}"')
                    # Исключаем явные служебные строки
                    if "%" not in decoded_text and "backurl" not in decoded_text:
                        decoded_texts.append(decoded_text)
                except json.JSONDecodeError:
                    continue

    top_ten_vacancies = valid_links[:10]
    vacancies_dict = {index: top_ten_vacancies for index, vacancy in enumerate(top_ten_vacancies)}
    #print(top_ten_vacancies)

    # Анализ зарплат (если они есть)
    avg_salary = "Недоступно"
    
    if salaries:
        salaries_full = [salary * 1000 for salary in salaries]
        # Находим среднее значение
        avg_salary = round(sum(salaries_full) / len(salaries_full), 2)
        #print(f"Средняя зарплата: {avg_salary}")
            
   

    # ТОП-10 компаний
    top_companies = Counter(companies).most_common(10)


    return {
        "vacancies": len(valid_links),
        "average_salary": avg_salary,
        "top_companies": top_companies,
        "links": vacancies_dict
    }

def send_links_in_batches(chat_id, links_dict, batch_size=5):
    # Преобразуем словарь в ОДИН СПИСОК ссылок
    links = [link for link_list in links_dict.values() for link in link_list]

    for i in range(0, len(links), batch_size):
        batch = links[i:i + batch_size]
        message = "\n".join(batch)
        bot.send_message(chat_id, message)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Москва", callback_data="Москва"))
    markup.add(types.InlineKeyboardButton("Санкт-Петербург", callback_data="Санкт-Петербург"))
    bot.send_message(message.chat.id, "Выберите регион:", reply_markup=markup)

# Обработчик нажатия кнопки региона
@bot.callback_query_handler(func=lambda call: call.data in regions)
def region_selection(call):
    region = call.data
    markup = types.InlineKeyboardMarkup()
    for level in levels:
        markup.add(types.InlineKeyboardButton(level, callback_data=f"{region}|{level}"))
    bot.edit_message_text(f"Вы выбрали {region}. Выберите уровень:", chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=markup)

# Обработчик выбора уровня
@bot.callback_query_handler(func=lambda call: '|' in call.data and len(call.data.split('|')) == 2)
def level_selection(call):
    region, level = call.data.split('|')
    markup = types.InlineKeyboardMarkup()
    for category in categories:
        markup.add(types.InlineKeyboardButton(category, callback_data=f"{region}|{level}|{category}"))
    bot.edit_message_text(f"Вы выбрали {level} уровень в {region}. Выберите категорию:", chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=markup)

# Обработчик выбора категории
@bot.callback_query_handler(func=lambda call: len(call.data.split('|')) == 3)
def category_selection(call):
    region, level, category = call.data.split('|')
    region_id = regions[region]
    level_id = levels[level]
    category_text = categories[category]

    vacancies_data = parse_vacancies(region_id, level_id, category_text)
    if vacancies_data["vacancies"] > 0:
        # Отправка статистики
        bot.send_message(
            call.message.chat.id, 
            f"📊 *Статистика по вакансиям:*\n"
            f"🔹 Найдено вакансий: {vacancies_data['vacancies']}\n"
            f"💰 Средняя зарплата: {vacancies_data['average_salary']} руб.\n"
            f"🏢 ТОП-3 компании:\n" + "\n".join([f"{c[0]} — {c[1]} вакансий" for c in vacancies_data["top_companies"][:3]]),
            parse_mode="Markdown"
        )
        send_links_in_batches(call.message.chat.id, vacancies_data["links"])
        bot.send_message(
            call.message.chat.id, "Для нового поиска введите /start", parse_mode="Markdown"
        )
    else:
        bot.send_message(call.message.chat.id, "Вакансии не найдены.")

# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True)