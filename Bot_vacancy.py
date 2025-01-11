import requests
import fake_useragent
from bs4 import BeautifulSoup
from telebot import TeleBot, types
import json

# Токен Telegram-бота
TOKEN = ""

# Доступные регионы и уровни опыта
regions = {"Москва": 1, "Санкт-Петербург": 2}
levels = {"Junior": "noExperience", "Middle": "between1And3", "Senior": "moreThan6"}
categories = {"Data Analyst": "Data+Analyst", "Data Scientist": "Data+Scientist", "Data Engineer": "Data+Engineer"}

# Инициализация бота
bot = TeleBot(TOKEN)

# Функция парсера
def parse_vacancies(region_id, level_id, category_text):
    #result = ""
    page_number = 0
    k = 0  # Счётчик вакансий
    hrefs = [] #Список ссылок на вакансии

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
            k += 1
            hre = item.find("a").get("href")
            hrefs.append(hre)

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
                
    return valid_links
    #for idx, link in enumerate(valid_links, start=1):
        #return(f"{idx}. {link}")
        
    '''# Получение первых десяти вакансий
    top_ten_vacancies = valid_links[:10]
    vacancies_dict = {index: top_ten_vacancies for index, vacancy in enumerate(top_ten_vacancies)}
    return vacancies_dict'''

def send_links_in_batches(chat_id, links, batch_size=5):
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
    bot.edit_message_text(f"Вы выбрали {region}.Выберите уровень:", chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=markup)

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

    vacancies = parse_vacancies(region_id, level_id, category_text)
    if vacancies:
        send_links_in_batches(call.message.chat.id, vacancies)
    else:
        bot.send_message(call.message.chat.id, "Вакансии не найдены.")
        
# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True)