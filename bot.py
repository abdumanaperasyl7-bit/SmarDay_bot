import telebot
from datetime import datetime, timedelta

TOKEN = ".................."
bot = telebot.TeleBot(TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {"step": "ask_age"}
    bot.send_message(chat_id, "Привет! Я SmartDay Bot 🤖\nДавай составим твой идеальный день! Сколько тебе лет?")

@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text
    data = user_data.get(chat_id, {})

    step = data.get("step")

    try:
        if step == "ask_age":
            if text.isdigit():
                data["age"] = int(text)
                data["step"] = "wake_time"
                bot.send_message(chat_id, "Во сколько ты обычно встаёшь? (например, 7:00)")
            else:
                bot.send_message(chat_id, "Пожалуйста, введи цифрами свой возраст.")
            return

        if step == "wake_time":
            data["wake_time"] = datetime.strptime(text, "%H:%M")
            data["step"] = "school_leave"
            bot.send_message(chat_id, "Во сколько ты идёшь в школу? (например, 8:00)")
            return

        if step == "school_leave":
            data["school_leave"] = datetime.strptime(text, "%H:%M")
            data["step"] = "school_return"
            bot.send_message(chat_id, "Во сколько ты приходишь домой со школы? (например, 14:00)")
            return

        if step == "school_return":
            data["school_return"] = datetime.strptime(text, "%H:%M")
            data["step"] = "sleep_time"
            bot.send_message(chat_id, "Во сколько ты ложишься спать? (например, 22:30)")
            return

        if step == "sleep_time":
            data["sleep_time"] = datetime.strptime(text, "%H:%M")
            data["step"] = "study_hours"
            bot.send_message(chat_id, "Сколько часов хочешь уделять учебе дома? (например, 2)")
            return

        if step == "study_hours":
            if text.isdigit():
                data["study_hours"] = int(text)
                data["step"] = "sport_hours"
                bot.send_message(chat_id, "Сколько часов хочешь уделять спорту?")
            else:
                bot.send_message(chat_id, "Пожалуйста, введи число часов.")
            return

        if step == "sport_hours":
            if text.isdigit():
                data["sport_hours"] = int(text)
                data["step"] = "hobby_hours"
                bot.send_message(chat_id, "Сколько часов хочешь уделять хобби?")
            else:
                bot.send_message(chat_id, "Пожалуйста, введи число часов.")
            return

        if step == "hobby_hours":
            if text.isdigit():
                data["hobby_hours"] = int(text)
                data["step"] = "rest_hours"
                bot.send_message(chat_id, "Сколько часов хочешь отдыхать дома?")
            else:
                bot.send_message(chat_id, "Пожалуйста, введи число часов.")
            return

        if step == "rest_hours":
            if text.isdigit():
                data["rest_hours"] = int(text)
                # Генерация расписания
                schedule = generate_full_schedule(data)
                bot.send_message(chat_id, schedule)
                data["step"] = "done"
            else:
                bot.send_message(chat_id, "Пожалуйста, введи число часов.")
            return

        if step == "done":
            bot.send_message(chat_id, "Если хочешь составить новый день, напиши /start.")

    except Exception as e:
        bot.send_message(chat_id, f"Произошла ошибка: {e}. Попробуй ещё раз /start")


def generate_full_schedule(data):
    lines = []

    wake = data["wake_time"]
    school_leave = data["school_leave"]
    school_return = data["school_return"]
    sleep = data["sleep_time"]

    
    lines.append(f"{wake.strftime('%H:%M')} - {(wake + timedelta(minutes=15)).strftime('%H:%M')}: Подъём и умывание")
    lines.append(f"{(wake + timedelta(minutes=15)).strftime('%H:%M')} - {(wake + timedelta(minutes=30)).strftime('%H:%M')}: Зарядка")
    lines.append(f"{(wake + timedelta(minutes=30)).strftime('%H:%M')} - {school_leave.strftime('%H:%M')}: Завтрак и подготовка к школе")

    
    lines.append(f"{school_leave.strftime('%H:%M')} - {school_return.strftime('%H:%M')}: Школа")

    
    current = school_return
    # Отдых
    if data["rest_hours"] > 0:
        rest_end = current + timedelta(hours=data["rest_hours"])
        lines.append(f"{current.strftime('%H:%M')} - {rest_end.strftime('%H:%M')}: Отдых дома (слушай музыку, хобби)")
        current = rest_end

    
    if data["study_hours"] > 0:
        study_end = current + timedelta(hours=data["study_hours"])
        lines.append(f"{current.strftime('%H:%M')} - {study_end.strftime('%H:%M')}: Учёба (уроки, домашки, английский)")
        current = study_end

    
    if data["sport_hours"] > 0:
        sport_end = current + timedelta(hours=data["sport_hours"])
        lines.append(f"{current.strftime('%H:%M')} - {sport_end.strftime('%H:%M')}: Спорт / прогулка")
        current = sport_end

    
    if data["hobby_hours"] > 0:
        hobby_end = current + timedelta(hours=data["hobby_hours"])
        lines.append(f"{current.strftime('%H:%M')} - {hobby_end.strftime('%H:%M')}: Хобби / свободное время")
        current = hobby_end

    
    lines.append(f"{(sleep - timedelta(minutes=60)).strftime('%H:%M')} - {sleep.strftime('%H:%M')}: Ужин, душ, подготовка ко сну")
    lines.append(f"{sleep.strftime('%H:%M')} - {(sleep + timedelta(hours=0)).strftime('%H:%M')}: Сон")

    lines.append("\n💡 Совет: чередуй учёбу, отдых, спорт и хобби. Делай перерывы каждые 1-2 часа.")

    return "\n".join(lines)

bot.polling(none_stop=True, timeout=100)
