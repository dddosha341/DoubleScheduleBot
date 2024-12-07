import os
from datetime import datetime, timedelta
import pytz
from telegram import Bot
from telegram.constants import ParseMode
import asyncio

# Ваш токен бота, полученный у BotFather
TOKEN = ''
CHANNEL_ID = ''
MESSAGE_ID = 12345

# Часовой пояс (Московское время)
MSK = pytz.timezone('Europe/Moscow')

# Перевод дней недели на русский
DAYS_IN_RUSSIAN = {
    "Monday": "Понедельник",
    "Tuesday": "Вторник",
    "Wednesday": "Среда",
    "Thursday": "Четверг",
    "Friday": "Пятница",
    "Saturday": "Суббота",
    "Sunday": "Воскресенье",
}
# Функция для определения файла расписания
def get_schedule_file(current_time):
    day_of_week = current_time.weekday()  # День недели (0=понедельник, 6=воскресенье)
    hour = current_time.hour

    # После 18:00 выдаем расписание на следующий день
    if hour >= 18:
        # Если сегодня суббота, выдаем расписание на понедельник
        if day_of_week == 5:  # Суббота
            return "monday.txt"
        # Если воскресенье, ничего не делаем
        elif day_of_week == 6:  # Воскресенье
            return None
        else:
            files = ["monday.txt", "tuesday.txt", "wednesday.txt", "thursday.txt", "friday.txt", "saturday.txt"]
            return files[(day_of_week + 1) % 7]
    else:
        # До 18:00 выдаем расписание на текущий день
        files = ["monday.txt", "tuesday.txt", "wednesday.txt", "thursday.txt", "friday.txt", "saturday.txt"]
        return files[day_of_week]

# Функция для чтения расписания из файла
def read_schedule(file_name):
    if not os.path.exists(file_name):
        return None

    with open(file_name, "r", encoding="utf-8") as file:
        lines = file.readlines()

    schedule = []
    current_subject = {}

    for line in lines:
        line = line.strip()
        if line.isdigit():  # Номер пары
            if current_subject:
                schedule.append(current_subject)
            current_subject = {"number": line}
        elif "number" in current_subject and "name" not in current_subject:
            current_subject["name"] = line
        elif "name" in current_subject and "time" not in current_subject:
            current_subject["time"] = line
        elif "time" in current_subject and "place" not in current_subject:
            current_subject["place"] = line
        elif "place" in current_subject and "teacher" not in current_subject:
            current_subject["teacher"] = line

    if current_subject:
        schedule.append(current_subject)

    return schedule

# Функция для формирования текста сообщения
def format_message(schedule, target_date):
    day_name_en = target_date.strftime("%A")  # День недели (на английском)
    day_name_ru = DAYS_IN_RUSSIAN.get(day_name_en, day_name_en)  # Перевод на русский
    date_str = target_date.strftime("%d.%m.%Y")  # Дата

    message = f"🎓 **Актуальное расписание на {date_str} ({day_name_ru}):**\n\n"

    for subject in schedule:
        message += (
            f"**{subject['number']}. {subject['name']}**\n"
            f"    _Начало:_ {subject['time']}\n"
            f"    _Место:_ {subject['place']}\n"
            f"    _Преподаватель:_ {subject['teacher']}\n\n"
        )

    message += "#расписание #актуальноерасписание"
    return message

# Основная функция для обновления сообщения
async def update_schedule():
    now = datetime.now(MSK)
    schedule_file = get_schedule_file(now)
    if not schedule_file:
        print("Сегодня воскресенье, ничего не обновляем.")
        return

    schedule = read_schedule(schedule_file)
    if not schedule:
        print(f"Файл {schedule_file} не найден или пуст.")
        return

    # Формируем сообщение
    target_date = now + timedelta(days=1) if now.hour >= 18 else now
    message = format_message(schedule, target_date)

    # Обновляем сообщение в канале
    bot = Bot(token=TOKEN)
    await bot.edit_message_text(chat_id=CHANNEL_ID, message_id=MESSAGE_ID, text=message, parse_mode=ParseMode.HTML)
    print(f"Сообщение с ID {MESSAGE_ID} обновлено!")

# Запуск асинхронной функции
if __name__ == "__main__":
    asyncio.run(update_schedule())
