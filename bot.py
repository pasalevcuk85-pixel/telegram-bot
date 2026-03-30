import os
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Тимчасова база вакансій
JOBS = [
    {
        "title": "Кухар",
        "city": "Відень",
        "category": "Ресторани",
        "salary": "2200€",
        "description": "Робота в ресторані, досвід від 1 року.",
        "contact": "@hr_vienna_food"
    },
    {
        "title": "Офіціант",
        "city": "Відень",
        "category": "Ресторани",
        "salary": "1900€ + чайові",
        "description": "Потрібен офіціант у центр Відня.",
        "contact": "@jobs_center_vienna"
    },
    {
        "title": "Барбер",
        "city": "Відень",
        "category": "Барбершоп",
        "salary": "2500€",
        "description": "Шукаємо барбера з досвідом і своєю базою плюс.",
        "contact": "@barberteam_vienna"
    },
    {
        "title": "Прибиральник",
        "city": "Відень",
        "category": "Клінінг",
        "salary": "1800€",
        "description": "Прибирання офісів, ранкові зміни.",
        "contact": "@clean_work_vienna"
    },
    {
        "title": "Кур'єр",
        "city": "Відень",
        "category": "Доставка",
        "salary": "2100€",
        "description": "Доставка їжі, велосипед надається.",
        "contact": "@delivery_vienna_jobs"
    },
    {
        "title": "Кухар",
        "city": "Грац",
        "category": "Ресторани",
        "salary": "2100€",
        "description": "Ресторан шукає кухаря на повну ставку.",
        "contact": "@graz_food_jobs"
    },
    {
        "title": "Бариста",
        "city": "Зальцбург",
        "category": "Кафе",
        "salary": "1850€",
        "description": "Кав'ярня в центрі шукає бариста.",
        "contact": "@salzburg_cafe_jobs"
    },
]

CITIES = ["Відень", "Грац", "Зальцбург"]
CATEGORIES = ["Ресторани", "Барбершоп", "Клінінг", "Доставка", "Кафе"]

# Стан користувачів
user_state = {}
# Приклад:
# user_state[user_id] = {
#   "city": "Відень",
#   "category": "Ресторани",
#   "results": [...],
#   "index": 0
# }


def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔎 Знайти роботу")
    markup.row("📋 Мої фільтри", "♻️ Скинути пошук")
    return markup


def cities_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for city in CITIES:
        markup.row(city)
    markup.row("⬅️ Назад")
    return markup


def categories_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for category in CATEGORIES:
        markup.row(category)
    markup.row("⬅️ Назад")
    return markup


def results_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("➡️ Ще вакансії")
    markup.row("♻️ Скинути пошук", "⬅️ Головне меню")
    return markup


def filter_jobs(city: str, category: str):
    return [
        job for job in JOBS
        if job["city"] == city and job["category"] == category
    ]


def format_job(job: dict, number: int, total: int):
    return (
        f"💼 Вакансія {number}/{total}\n\n"
        f"📌 Посада: {job['title']}\n"
        f"🏙 Місто: {job['city']}\n"
        f"📂 Сфера: {job['category']}\n"
        f"💰 Зарплата: {job['salary']}\n\n"
        f"📝 Опис: {job['description']}\n"
        f"📲 Контакт: {job['contact']}"
    )


def send_next_job(chat_id: int, user_id: int):
    state = user_state.get(user_id)

    if not state or not state.get("results"):
        bot.send_message(
            chat_id,
            "Немає активного пошуку. Натисни: 🔎 Знайти роботу",
            reply_markup=main_menu()
        )
        return

    index = state.get("index", 0)
    results = state["results"]

    if index >= len(results):
        bot.send_message(
            chat_id,
            "Більше вакансій поки немає. Можеш змінити пошук або скинути фільтри.",
            reply_markup=results_menu()
        )
        return

    job = results[index]
    bot.send_message(
        chat_id,
        format_job(job, index + 1, len(results)),
        reply_markup=results_menu()
    )
    state["index"] = index + 1


@bot.message_handler(commands=["start"])
def start_command(message):
    user_state[message.from_user.id] = {}
    bot.send_message(
        message.chat.id,
        "Привіт 👋 Я бот для пошуку роботи в Австрії.\n\n"
        "Натисни: 🔎 Знайти роботу",
        reply_markup=main_menu()
    )


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text.strip()

    if user_id not in user_state:
        user_state[user_id] = {}

    state = user_state[user_id]

    if text == "🔎 Знайти роботу":
        state.clear()
        state["step"] = "choose_city"
        bot.send_message(
            message.chat.id,
            "Оберіть місто:",
            reply_markup=cities_menu()
        )
        return

    if text == "📋 Мої фільтри":
        city = state.get("city", "не вибрано")
        category = state.get("category", "не вибрано")
        bot.send_message(
            message.chat.id,
            f"Твої фільтри:\n🏙 Місто: {city}\n📂 Сфера: {category}",
            reply_markup=main_menu()
        )
        return

    if text == "♻️ Скинути пошук":
        user_state[user_id] = {}
        bot.send_message(
            message.chat.id,
            "Пошук скинуто. Можемо почати заново.",
            reply_markup=main_menu()
        )
        return

    if text == "⬅️ Головне меню":
        bot.send_message(
            message.chat.id,
            "Повернулись у головне меню.",
            reply_markup=main_menu()
        )
        return

    if text == "⬅️ Назад":
        step = state.get("step")
        if step == "choose_category":
            state["step"] = "choose_city"
            bot.send_message(
                message.chat.id,
                "Оберіть місто:",
                reply_markup=cities_menu()
            )
            return
        bot.send_message(
            message.chat.id,
            "Головне меню.",
            reply_markup=main_menu()
        )
        return

    if text == "➡️ Ще вакансії":
        send_next_job(message.chat.id, user_id)
        return

    if state.get("step") == "choose_city" and text in CITIES:
        state["city"] = text
        state["step"] = "choose_category"
        bot.send_message(
            message.chat.id,
            f"Місто: {text}\n\nТепер обери сферу:",
            reply_markup=categories_menu()
        )
        return

    if state.get("step") == "choose_category" and text in CATEGORIES:
        state["category"] = text
        state["results"] = filter_jobs(state["city"], state["category"])
        state["index"] = 0
        state["step"] = "show_results"

        if not state["results"]:
            bot.send_message(
                message.chat.id,
                "Поки що немає вакансій за твоїм запитом 😔\n"
                "Спробуй інше місто або іншу сферу.",
                reply_markup=main_menu()
            )
            return

        bot.send_message(
            message.chat.id,
            f"Знайшов {len(state['results'])} вакансій.\nПоказую першу:",
            reply_markup=results_menu()
        )
        send_next_job(message.chat.id, user_id)
        return

    bot.send_message(
        message.chat.id,
        "Я не зрозумів команду 😅 Натисни кнопку з меню.",
        reply_markup=main_menu()
    )


bot.infinity_polling()
