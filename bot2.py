import sqlite3
from datetime import datetime, timedelta, date, time

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

TOKEN = "8829432242:AAFe35yxvOul7l3JE25fgE7k_tJvD87heMo"

# Чат для розсилки нагадувань (якщо є груповий чат)
NOTIFICATION_CHAT_ID = None  # Встав ID чату або залиш None для відключення

# -----------------------------
# Стан діалогів
# -----------------------------
DATE_FOR_SHIFT = 1
PERSON_1_FOR_SHIFT = 2
PERSON_2_FOR_SHIFT = 3
DATE_FOR_REMOVE = 4
PERSON_FOR_REMOVE = 5
EDIT_BIRTHDAY_NAME = 10
EDIT_BIRTHDAY_DATE = 11

MAIN_KEYBOARD = [
    ["Додати мене", "Список людей"],
    ["Додати чергування", "Видалити чергування"],
    ["Чергуємо на сьогодні", "Чергуємо завтра"],
    ["Хто чергує сьогодні", "Хто чергує завтра"],
    ["Чергуємо на тиждень", "Редагувати ДР"],
]

# -----------------------------
# Дати народження
# -----------------------------
BIRTHDAYS = {
    "Андрушак Анна": "21.12.2010",
    "Боровик Михайло": "19.11.2010",
    "Бочуляк Анастасія": "06.08.2010",
    "Володько Сергій": "13.10.2010",
    "Гаврилюк Соломія": "02.05.2011",
    "Грицюк Дмитро": "20.09.2011",
    "Дударчук Віра": "09.06.2011",
    "Живанюк Ілля": "11.03.2011",
    "Зозулевич Євгенія": "18.10.2010",
    "Жук Дмитро": "09.11.2010",
    "Жуковський Владислав": "06.10.2011",
    "Касянчик Ніка": "26.11.2010",
    "Кициляк Дмитро": "29.06.2011",
    "Коржан Олександр": "15.10.2010",
    "Корніюк Софія": "09.06.2011",
    "Крупко Микола": "29.09.2010",
    "Литвинчук Соломія": "12.06.2011",
    "Маркова Аліна": "12.10.2011",
    "Маркович Святослав": "27.02.2011",
    "Мосніцький Тимофій": "01.10.2011",
    "Навроцький Владислав": "11.02.2011",
    "Омельчук Олексій": "25.02.2011",
    "Павлюк Марія": "03.04.2011",
    "Поліщук Марк": "25.02.2011",
    "Примін Максим": "13.02.2011",
    "Реньжина Віолетта": "02.07.2011",
    "Тарасюк Андрій": "21.01.2011",
    "Ткач Владислав": "24.04.2010",
    "Трофімчук Максим": "19.01.2011",
    "Чуйко Михайло": "19.01.2011",
    "Шевченко Максим": "28.10.2010",
    "Штихалюк Дарина": "18.11.2010",
}

# -----------------------------
# Стандартний графік чергувань
# -----------------------------
DEFAULT_SCHEDULE = [
    ("2026-10-12", ("Касянчик Ніка", "Дударчук Віра")),
    ("2026-10-13", ("Шевченко Максим", "Примін Максим")),
    ("2026-10-14", ("Литвинчук Соломія", "Корніюк Софія")),
    ("2026-10-15", ("Володько Сергій", "Крупко Микола")),
    ("2026-10-16", ("Боровик Михайло", "Чуйко Михайло")),
    ("2026-10-17", ("Ткач Владислав", "Тарасюк Андрій")),
    ("2026-10-19", ("Реньжина Віолетта", "Гаврилюк Соломія")),
    ("2026-10-20", ("Зозулевич Євгенія", "Штихалюк Дарина")),
    ("2026-10-21", ("Бочуляк Анастасія", "Павлюк Марія")),
    ("2026-10-22", ("Грицюк Дмитро", "Живанюк Ілля")),
    ("2026-10-23", ("Жук Дмитро", "Коржан Олександр")),
    ("2026-10-24", ("Кициляк Дмитро", "Жуковський Владислав")),
    ("2026-10-26", ("Маркович Святослав", "Навроцький Владислав")),
    ("2026-10-27", ("Омельчук Олексій", "Поліщук Марк")),
    ("2026-10-28", ("Трофімчук Максим", "Мосніцький Тимофій")),
    ("2026-10-29", ("Андрушак Анна", "Маркова Аліна")),
    ("2026-10-30", ("Касянчик Ніка", "Дударчук Віра")),
    ("2026-10-31", ("Шевченко Максим", "Примін Максим")),
    ("2026-11-02", ("Литвинчук Соломія", "Корніюк Софія")),
    ("2026-11-03", ("Володько Сергій", "Крупко Микола")),
    ("2026-11-04", ("Боровик Михайло", "Чуйко Михайло")),
    ("2026-11-05", ("Ткач Владислав", "Тарасюк Андрій")),
    ("2026-11-06", ("Реньжина Віолетта", "Гаврилюк Соломія")),
    ("2026-11-07", ("Зозулевич Євгенія", "Штихалюк Дарина")),
    ("2026-11-09", ("Бочуляк Анастасія", "Павлюк Марія")),
    ("2026-11-10", ("Грицюк Дмитро", "Живанюк Ілля")),
    ("2026-11-11", ("Жук Дмитро", "Коржан Олександр")),
    ("2026-11-12", ("Кициляк Дмитро", "Жуковський Владислав")),
    ("2026-11-13", ("Маркович Святослав", "Навроцький Владислав")),
    ("2026-11-14", ("Омельчук Олексій", "Поліщук Марк")),
    ("2026-11-16", ("Трофімчук Максим", "Мосніцький Тимофій")),
    ("2026-11-17", ("Андрушак Анна", "Маркова Аліна")),
    ("2026-11-18", ("Касянчик Ніка", "Дударчук Віра")),
    ("2026-11-19", ("Шевченко Максим", "Примін Максим")),
    ("2026-11-20", ("Литвинчук Соломія", "Корніюк Софія")),
    ("2026-11-21", ("Володько Сергій", "Крупко Микола")),
    ("2026-11-23", ("Боровик Михайло", "Чуйко Михайло")),
    ("2026-11-24", ("Ткач Владислав", "Тарасюк Андрій")),
    ("2026-11-25", ("Реньжина Віолетта", "Гаврилюк Соломія")),
    ("2026-11-26", ("Зозулевич Євгенія", "Штихалюк Дарина")),
    ("2026-11-27", ("Бочуляк Анастасія", "Павлюк Марія")),
    ("2026-11-28", ("Грицюк Дмитро", "Живанюк Ілля")),
    ("2026-11-30", ("Жук Дмитро", "Коржан Олександр")),
]

# -----------------------------
# SQLite helpers
# -----------------------------
def get_connection():
    conn = sqlite3.connect("duty_bot.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            username TEXT,
            full_name TEXT UNIQUE NOT NULL,
            birthday TEXT DEFAULT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            duty_date TEXT NOT NULL,
            person_id INTEGER NOT NULL,
            slot INTEGER NOT NULL CHECK(slot IN (1, 2)),
            UNIQUE(duty_date, slot)
        )
    """)
    conn.commit()
    conn.close()


def clean_name(name: str) -> str:
    return " ".join(name.strip().split())


def get_or_create_person(full_name: str):
    full_name = clean_name(full_name)
    if not full_name:
        return None

    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM people WHERE full_name = ?",
        (full_name,)
    ).fetchone()
    if row:
        conn.close()
        return row

    conn.execute(
        "INSERT INTO people (user_id, username, full_name, birthday) VALUES (NULL, ?, ?, NULL)",
        (full_name.lower().replace(" ", "_"), full_name),
    )
    conn.commit()
    person = conn.execute(
        "SELECT * FROM people WHERE full_name = ?",
        (full_name,)
    ).fetchone()
    conn.close()
    return person


def add_person_from_user(user_id: int, username: str, full_name: str):
    full_name = clean_name(full_name)
    if not full_name:
        return

    conn = get_connection()
    row = conn.execute("SELECT * FROM people WHERE full_name = ?", (full_name,)).fetchone()
    if not row:
        conn.execute(
            """
            INSERT INTO people (user_id, username, full_name, birthday)
            VALUES (?, ?, ?, NULL)
            """,
            (user_id, username or "без_нікнейму", full_name),
        )
    else:
        conn.execute(
            """
            UPDATE people
            SET user_id = ?, username = ?
            WHERE full_name = ?
            """,
            (user_id, username or "без_нікнейму", full_name),
        )
    conn.commit()
    conn.close()


def get_person_by_name(name: str):
    name = clean_name(name)
    if not name:
        return None

    q = name.lower()
    conn = get_connection()
    person = conn.execute(
        """
        SELECT * FROM people
        WHERE LOWER(full_name) = ?
           OR LOWER(full_name) LIKE ?
           OR LOWER(username) = ?
        """,
        (q, f"%{q}%", q),
    ).fetchone()
    conn.close()
    return person


def get_all_people():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, user_id, username, full_name, birthday FROM people ORDER BY full_name"
    ).fetchall()
    conn.close()
    return rows


def get_person_by_user_id(user_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM people WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return row


def set_person_birthday(full_name: str, birthday: str):
    full_name = clean_name(full_name)
    if not full_name:
        return False

    try:
        datetime.strptime(birthday, "%d.%m.%Y")
    except ValueError:
        return False

    conn = get_connection()
    conn.execute(
        "UPDATE people SET birthday = ? WHERE full_name = ?",
        (birthday, full_name),
    )
    conn.commit()
    conn.close()
    return True


def get_person_birthday(full_name: str):
    full_name = clean_name(full_name)
    if not full_name:
        return "невідомо"

    conn = get_connection()
    row = conn.execute(
        "SELECT birthday FROM people WHERE full_name = ?",
        (full_name,),
    ).fetchone()
    conn.close()

    if row and row["birthday"]:
        return row["birthday"]
    return BIRTHDAYS.get(full_name, "невідомо")


def add_shift_for_date(date_str: str, slot: int, person_id: int):
    conn = get_connection()
    conn.execute(
        """
        INSERT OR REPLACE INTO shifts (duty_date, person_id, slot)
        VALUES (?, ?, ?)
        """,
        (date_str, person_id, slot),
    )
    conn.commit()
    conn.close()


def remove_shift_for_date(date_str: str, slot: int):
    conn = get_connection()
    conn.execute("DELETE FROM shifts WHERE duty_date = ? AND slot = ?", (date_str, slot))
    conn.commit()
    conn.close()


def get_shift_by_slot(date_str: str, slot: int):
    conn = get_connection()
    row = conn.execute(
        """
        SELECT p.full_name, p.username
        FROM shifts s
        JOIN people p ON p.id = s.person_id
        WHERE s.duty_date = ? AND s.slot = ?
        """,
        (date_str, slot),
    ).fetchone()
    conn.close()
    return row


def get_day_shift(date_str: str):
    names = []
    for slot in (1, 2):
        row = get_shift_by_slot(date_str, slot)
        names.append(row["full_name"] if row else "вільно")
    return names


def format_date_human(date_str: str) -> str:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y")
    except ValueError:
        return date_str


def get_week_schedule(start_date: str):
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
    except ValueError:
        return []

    records = []
    for i in range(7):
        d = start + timedelta(days=i)
        d_str = d.strftime("%Y-%m-%d")
        records.append((d_str, get_day_shift(d_str)))
    return records


def populate_default_schedule():
    conn = get_connection()
    for date_str, names in DEFAULT_SCHEDULE:
        for slot, name in enumerate(names, start=1):
            full_name = clean_name(name)
            person = conn.execute("SELECT * FROM people WHERE full_name = ?", (full_name,)).fetchone()
            if not person:
                conn.execute(
                    "INSERT INTO people (user_id, username, full_name, birthday) VALUES (NULL, ?, ?, NULL)",
                    (full_name.lower().replace(" ", "_"), full_name),
                )
                person = conn.execute("SELECT * FROM people WHERE full_name = ?", (full_name,)).fetchone()

            conn.execute(
                """
                INSERT OR IGNORE INTO shifts(duty_date, person_id, slot)
                VALUES (?, ?, ?)
                """,
                (date_str, person["id"], slot),
            )
    conn.commit()
    conn.close()


# -----------------------------
# Display functions
# -----------------------------
def get_day_text(date_str: str) -> str:
    names = get_day_shift(date_str)
    return (
        f"Чергування на {format_date_human(date_str)}:\n"
        f"1. {names[0]}\n"
        f"2. {names[1]}"
    )


def get_week_text(start_date: str) -> str:
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
    except ValueError:
        return "Некоректна дата. Введіть дату у форматі YYYY-MM-DD."

    lines = []
    for i in range(7):
        d = start + timedelta(days=i)
        d_str = d.strftime("%Y-%m-%d")
        names = get_day_shift(d_str)
        lines.append(f"{format_date_human(d_str)}: {names[0]} / {names[1]}")
    return "\n".join(lines)


def who_is_on_duty_text(date_str: str) -> str:
    names = get_day_shift(date_str)
    return (
        f"Чергують {format_date_human(date_str)}:\n"
        f"1. {names[0]}\n"
        f"2. {names[1]}"
    )


# -----------------------------
# Автоматичні нагадування
# -----------------------------
async def send_morning_notification(context: ContextTypes.DEFAULT_TYPE):
    today = date.today().strftime("%Y-%m-%d")
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")

    today_names = get_day_shift(today)
    tomorrow_names = get_day_shift(tomorrow)

    text = (
        "📌 Добрий ранок!\n\n"
        "Чергування на сьогодні:\n"
        f"1. {today_names[0]}\n"
        f"2. {today_names[1]}\n\n"
        "Чергування на завтра:\n"
        f"1. {tomorrow_names[0]}\n"
        f"2. {tomorrow_names[1]}"
    )

    if NOTIFICATION_CHAT_ID:
        try:
            await context.bot.send_message(chat_id=NOTIFICATION_CHAT_ID, text=text)
        except Exception as e:
            print(f"Помилка при відправці ранкового повідомлення: {e}")


async def send_evening_notification(context: ContextTypes.DEFAULT_TYPE):
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    tomorrow_names = get_day_shift(tomorrow)

    text = (
        "🌙 Добрий вечір!\n\n"
        "Нагадування: завтра чергують:\n"
        f"1. {tomorrow_names[0]}\n"
        f"2. {tomorrow_names[1]}"
    )

    if NOTIFICATION_CHAT_ID:
        try:
            await context.bot.send_message(chat_id=NOTIFICATION_CHAT_ID, text=text)
        except Exception as e:
            print(f"Помилка при відправці вечірнього повідомлення: {e}")


# -----------------------------
# Basic handlers
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user:
        existing = get_person_by_user_id(user.id)
        if not existing:
            add_person_from_user(
                user.id,
                user.username or "без_нікнейму",
                user.full_name or user.username or "Невідомий",
            )

    keyboard = ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)
    await update.message.reply_text(
        "Привіт! Я бот для списку чергувань.\n\n"
        "У кожен день є 2 чергових, як у твоєму графіку.",
        reply_markup=keyboard,
    )


async def add_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        await update.message.reply_text("Не вдалося визначити користувача.")
        return

    full_name = user.full_name or user.username or "Невідомий"
    add_person_from_user(user.id, user.username or "без_нікнейму", full_name)

    await update.message.reply_text(
        f"Ви додані до списку людей: {full_name}",
        reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True),
    )


async def list_people(update: Update, context: ContextTypes.DEFAULT_TYPE):
    people = get_all_people()
    if not people:
        await update.message.reply_text(
            "Поки немає людей у списку.",
            reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True),
        )
        return

    lines = ["Список людей:"]
    for idx, person in enumerate(people, 1):
        full_name = person["full_name"]
        birthday = person["birthday"] or BIRTHDAYS.get(full_name, "невідомо")
        lines.append(f"{idx}. {full_name} — {birthday}")
    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True),
    )


async def today_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = date.today().strftime("%Y-%m-%d")
    await update.message.reply_text(
        get_day_text(today),
        reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True),
    )


async def tomorrow_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    await update.message.reply_text(
        get_day_text(tomorrow),
        reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True),
    )


async def who_is_on_duty_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = date.today().strftime("%Y-%m-%d")
    await update.message.reply_text(
        who_is_on_duty_text(today),
        reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True),
    )


async def who_is_on_duty_tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    await update.message.reply_text(
        who_is_on_duty_text(tomorrow),
        reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True),
    )


async def week_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = date.today().strftime("%Y-%m-%d")
    await update.message.reply_text(
        get_week_text(today),
        reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True),
    )


# -----------------------------
# Додавання чергування
# -----------------------------
async def add_shift_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введіть дату чергування у форматі YYYY-MM-DD.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return DATE_FOR_SHIFT


async def add_shift_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    try:
        datetime.strptime(text, "%Y-%m-%d")
    except ValueError:
        await update.message.reply_text("Некоректна дата. Введіть дату у форматі YYYY-MM-DD.")
        return DATE_FOR_SHIFT

    context.user_data["shift_date"] = text
    await update.message.reply_text(
        f"Дата прийнята: {format_date_human(text)}\n\n"
        "Введіть 1-шу людину для чергування:",
        reply_markup=ReplyKeyboardRemove(),
    )
    return PERSON_1_FOR_SHIFT


async def add_shift_person_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    person_name = clean_name(update.message.text)
    person = get_person_by_name(person_name)
    if not person:
        await update.message.reply_text(
            "Такої людини немає в списку. Спробуйте ще раз."
        )
        return PERSON_1_FOR_SHIFT

    context.user_data["person_1"] = person["full_name"]
    await update.message.reply_text(
        f"1-ша людина: {person['full_name']}\n\n"
        "Введіть 2-гу людину для чергування:"
    )
    return PERSON_2_FOR_SHIFT


async def add_shift_person_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    person_name = clean_name(update.message.text)
    person = get_person_by_name(person_name)
    if not person:
        await update.message.reply_text(
            "Такої людини немає в списку. Спробуйте ще раз."
        )
        return PERSON_2_FOR_SHIFT

    date_str = context.user_data["shift_date"]
    person_1_name = context.user_data["person_1"]
    person_2_name = person["full_name"]

    p1 = get_person_by_name(person_1_name)
    p2 = get_person_by_name(person_2_name)

    if not p1 or not p2:
        await update.message.reply_text("Не вдалося знайти одну з людей.")
        context.user_data.clear()
        return ConversationHandler.END

    add_shift_for_date(date_str, 1, p1["id"])
    add_shift_for_date(date_str, 2, p2["id"])

    await update.message.reply_text(
        f"Чергування збережено на {format_date_human(date_str)}:\n"
        f"1. {p1['full_name']}\n"
        f"2. {p2['full_name']}",
        reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True),
    )

    context.user_data.clear()
    return ConversationHandler.END


# -----------------------------
# Видалення чергування
# -----------------------------
async def remove_shift_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введіть дату, для якої хочете видалити чергування у форматі YYYY-MM-DD.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return DATE_FOR_REMOVE


async def remove_shift_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date_str = update.message.text.strip()
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        await update.message.reply_text("Некоректна дата. Введіть дату у форматі YYYY-MM-DD.")
        return DATE_FOR_REMOVE

    context.user_data["remove_date"] = date_str
    current_names = get_day_shift(date_str)
    await update.message.reply_text(
        "Поточні чергові:\n"
        f"1. {current_names[0]}\n"
        f"2. {current_names[1]}\n\n"
        "Напишіть 'так' для підтвердження видалення або 'відміна' для скасування.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return PERSON_FOR_REMOVE


async def remove_shift_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = update.message.text.strip().lower()

    if response == "так":
        date_str = context.user_data["remove_date"]
        remove_shift_for_date(date_str, 1)
        remove_shift_for_date(date_str, 2)
        await update.message.reply_text(
            f"Чергування для {format_date_human(date_str)} видалено.",
            reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True),
        )
        context.user_data.clear()
        return ConversationHandler.END
    elif response == "відміна":
        await update.message.reply_text(
            "Видалення скасовано.",
            reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True),
        )
        context.user_data.clear()
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "Напишіть 'так' для підтвердження або 'відміна' для скасування."
        )
        return PERSON_FOR_REMOVE


# -----------------------------
# Редагування ДР
# -----------------------------
async def edit_birthday_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    people = get_all_people()
    if not people:
        await update.message.reply_text(
            "Немає людей для редагування.",
            reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True),
        )
        return ConversationHandler.END

    text = "Введіть повне ім'я людини, для якої хочете змінити дату народження:\n\n"
    text += "\n".join(f"{i + 1}. {p['full_name']}" for i, p in enumerate(people))
    await update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    return EDIT_BIRTHDAY_NAME


async def edit_birthday_name_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    full_name = clean_name(update.message.text)
    person = get_person_by_name(full_name)
    if not person:
        await update.message.reply_text("Такої людини немає в списку. Спробуйте ще раз.")
        return EDIT_BIRTHDAY_NAME

    context.user_data["target_person"] = person["full_name"]
    current_birthday = person["birthday"] or BIRTHDAYS.get(person["full_name"], "невідомо")
    await update.message.reply_text(
        f"Поточна дата народження для {person['full_name']}: {current_birthday}\n\n"
        "Введіть нову дату народження у форматі DD.MM.YYYY."
    )
    return EDIT_BIRTHDAY_DATE


async def edit_birthday_date_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    birthday = update.message.text.strip()
    try:
        datetime.strptime(birthday, "%d.%m.%Y")
    except ValueError:
        await update.message.reply_text("Некоректний формат. Введіть дату у форматі DD.MM.YYYY.")
        return EDIT_BIRTHDAY_DATE

    person_name = context.user_data.get("target_person")
    if not person_name:
        await update.message.reply_text(
            "Не вдалося визначити людину.",
            reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True),
        )
        return ConversationHandler.END

    if not set_person_birthday(person_name, birthday):
        await update.message.reply_text(
            "Не вдалося зберегти дату народження.",
            reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True),
        )
        context.user_data.clear()
        return ConversationHandler.END

    await update.message.reply_text(
        f"Дата народження для {person_name} збережена: {birthday}",
        reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True),
    )
    context.user_data.clear()
    return ConversationHandler.END


async def cancel_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Операцію скасовано.",
        reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True),
    )
    return ConversationHandler.END


# -----------------------------
# Кнопки / текст
# -----------------------------
async def handle_button_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "Додати мене":
        await add_me(update, context)
    elif text == "Список людей":
        await list_people(update, context)
    elif text == "Чергуємо на сьогодні":
        await today_schedule(update, context)
    elif text == "Чергуємо завтра":
        await tomorrow_schedule(update, context)
    elif text == "Хто чергує сьогодні":
        await who_is_on_duty_today(update, context)
    elif text == "Хто чергує завтра":
        await who_is_on_duty_tomorrow(update, context)
    elif text == "Чергуємо на тиждень":
        await week_schedule(update, context)
    elif text == "Редагувати ДР":
        return await edit_birthday_start(update, context)
    else:
        await update.message.reply_text(
            "Невідома команда. Оберіть дію з меню.",
            reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True),
        )


def main():
    init_db()
    populate_default_schedule()

    application = Application.builder().token(TOKEN).build()

    # Conversation handlers
    add_shift_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^Додати чергування$"), add_shift_start)
        ],
        states={
            DATE_FOR_SHIFT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_shift_date)],
            PERSON_1_FOR_SHIFT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_shift_person_1)],
            PERSON_2_FOR_SHIFT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_shift_person_2)],
        },
        fallbacks=[CommandHandler("cancel", cancel_flow)],
    )

    remove_shift_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^Видалити чергування$"), remove_shift_start)
        ],
        states={
            DATE_FOR_REMOVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, remove_shift_date)],
            PERSON_FOR_REMOVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, remove_shift_confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel_flow)],
    )

    edit_birthday_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^Редагувати ДР$"), edit_birthday_start)
        ],
        states={
            EDIT_BIRTHDAY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_birthday_name_step)],
            EDIT_BIRTHDAY_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_birthday_date_step)],
        },
        fallbacks=[CommandHandler("cancel", cancel_flow)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(add_shift_conv)
    application.add_handler(remove_shift_conv)
    application.add_handler(edit_birthday_conv)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_button_text))

    # Нагадування
    application.job_queue.run_daily(send_morning_notification, time=time(hour=8, minute=0))
    application.job_queue.run_daily(send_evening_notification, time=time(hour=20, minute=0))

    print("Бот запущено...")
    application.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()