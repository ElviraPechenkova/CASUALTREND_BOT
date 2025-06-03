import telebot
import json
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = '7685320374:AAH5eHCg7sg7a17lmfEMQaf0dyU6uyuyWHc'
bot = telebot.TeleBot(API_TOKEN)

user_data = {}

with open('clothes.json', encoding='utf-8') as f:
    catalog = json.load(f)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_data[message.chat.id] = {}
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Почати підбір образу"))
    bot.send_message(message.chat.id,
                     "Привіт! Я твій персональний стиліст від CasualTrend \U0001f9e5✨\nДопоможу підібрати ідеальний образ.\nГотова розпочати?",
                     reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "Почати підбір образу")
def ask_event(message):
    user_data[message.chat.id] = {}
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("На кожен день", "На побачення", "У подорож")
    markup.add("На роботу", "На святкову подію")
    bot.send_message(message.chat.id, "Куди ви шукаєте образ?", reply_markup=markup)
    bot.register_next_step_handler(message, ask_style)

def ask_style(message):
    user_data[message.chat.id]['event'] = message.text.strip().lower()
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Casual", "Класичний", "Спортивний")
    markup.add("Романтичний", "Streetstyle")
    bot.send_message(message.chat.id, "Який стиль вам ближчий?", reply_markup=markup)
    bot.register_next_step_handler(message, ask_type)

def ask_type(message):
    user_data[message.chat.id]['style'] = message.text.strip().lower()
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Верх", "Низ", "Повністю готовий образ")
    bot.send_message(message.chat.id, "Що саме хочете підібрати?", reply_markup=markup)
    bot.register_next_step_handler(message, ask_size_dispatcher)

def ask_size_dispatcher(message):
    user_data[message.chat.id]['type'] = message.text.strip().lower()
    if user_data[message.chat.id]['type'] == 'повністю готовий образ':
        ask_top_size(message)
    else:
        ask_single_size(message)

def ask_top_size(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("XS", "S", "M", "L", "XL", "XXL", "3XL")
    bot.send_message(message.chat.id, "Який ваш розмір верху?", reply_markup=markup)
    bot.register_next_step_handler(message, ask_bottom_size)

def ask_bottom_size(message):
    user_data[message.chat.id]['top_size'] = message.text.strip().upper()
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("XS", "S", "M", "L", "XL", "XXL", "3XL")
    bot.send_message(message.chat.id, "Який ваш розмір низу?", reply_markup=markup)
    bot.register_next_step_handler(message, ask_price)

def ask_single_size(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("XS", "S", "M", "L", "XL", "XXL", "3XL")
    bot.send_message(message.chat.id, "Який ваш розмір?", reply_markup=markup)
    bot.register_next_step_handler(message, ask_price)

def ask_price(message):
    if user_data[message.chat.id]['type'] == 'повністю готовий образ':
        user_data[message.chat.id]['bottom_size'] = message.text.strip().upper()
    else:
        user_data[message.chat.id]['size'] = message.text.strip().upper()
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("До 1000 грн", "Понад 1000 грн")
    bot.send_message(message.chat.id, "Оберіть бажану цінову категорію:", reply_markup=markup)
    bot.register_next_step_handler(message, ask_season)

def ask_season(message):
    user_data[message.chat.id]['price'] = message.text.strip()
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Весна/літо ☀️", "Осінь/зима ❄️")
    bot.send_message(message.chat.id, "Який сезон вас цікавить?", reply_markup=markup)
    bot.register_next_step_handler(message, ask_accent)

def ask_accent(message):
    season_text = message.text.strip().lower()
    if 'весна' in season_text:
        season = 'весна'
    elif 'осінь' in season_text:
        season = 'осінь'
    else:
        season = season_text
    user_data[message.chat.id]['season'] = season

    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Хочу акцент на кольорі", "Більше базових речей", "Щось трендове")
    bot.send_message(message.chat.id, "Що для вас важливіше у цьому підборі?", reply_markup=markup)
    bot.register_next_step_handler(message, show_result)

def show_result(message):
    accent_text = message.text.strip().lower()
    if 'кольор' in accent_text:
        accent = 'кольор'
    elif 'базов' in accent_text:
        accent = 'базове'
    elif 'тренд' in accent_text:
        accent = 'тренд'
    else:
        accent = accent_text
    user_data[message.chat.id]['accent'] = accent

    data = user_data[message.chat.id]
    price_range = data['price']

    results = []
    for item in catalog:
        if data['type'] == 'повністю готовий образ':
            size_match = data['top_size'] in item['sizes'] or data['bottom_size'] in item['sizes']
        else:
            size_match = data['size'] in item['sizes']

        price_value = item.get('price_uah', 0)
        price_check = (price_range == 'До 1000 грн' and price_value <= 1000) or (price_range == 'Понад 1000 грн' and price_value > 1000)

        if data['type'] in item['type'].lower() \
           and data['style'] in item['style'].lower() \
           and any(data['event'] in e.lower() for e in item['event']) \
           and any(data['season'] in s.lower() for s in item['season']) \
           and size_match \
           and price_check \
           and data['accent'] in item['accent'].lower():
            results.append(item)

    if results:
        bot.send_message(message.chat.id, "Ось що я підібрала для вас:")
        for item in results[:2] if data['type'] == 'повністю готовий образ' else results[:5]:
            image_url = item['image']
            price_info = item.get('price_uah', 'Ціна не вказана')

            url = item.get('url')
            url_top = item.get('url_top')
            url_bottom = item.get('url_bottom')

            if url:
                full_url = f"\U0001f449 {url}"
            elif url_top and url_bottom:
                full_url = f"\U0001f517 Верх: {url_top}\n\U0001f517 Низ: {url_bottom}"
            elif url_top:
                full_url = f"\U0001f517 Верх: {url_top}"
            elif url_bottom:
                full_url = f"\U0001f517 Низ: {url_bottom}"
            else:
                full_url = "Посилання не вказано"

            try:
                bot.send_photo(
                    message.chat.id,
                    image_url,
                    caption=f"{item['name']}\nЦіна: {price_info} грн\n{full_url}"
                )
            except Exception as e:
                bot.send_message(message.chat.id, f"❗ Не вдалося завантажити зображення для {item['name']}\nПричина: {e}")

        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Так, дякую", "Ні, спробувати ще раз")
        bot.send_message(message.chat.id, "Чи допомогли ми вам підібрати одяг?", reply_markup=markup)
        bot.register_next_step_handler(message, handle_feedback)
    else:
        bot.send_message(message.chat.id, "На жаль, не знайшла речей за вашими параметрами \U0001f614")
        ask_event(message)

def handle_feedback(message):
    text = message.text.strip().lower()
    if "так" in text:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton("Почати підбір образу"))
        bot.send_message(
            message.chat.id,
            "Раді були допомогти! \U0001f9e1\nЯкщо бажаєте підібрати ще — натисніть кнопку нижче або /start",
            reply_markup=markup
        )
    else:
        bot.send_message(message.chat.id, "Давайте спробуємо ще раз \U0001f447")
        ask_event(message)

bot.polling(none_stop=True, skip_pending=True)
