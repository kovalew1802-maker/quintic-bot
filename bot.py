import math
import os
import telebot
from telebot import types

# Получение токена из переменных окружения
TOKEN = (
    os.getenv("BOT_TOKEN")
    or os.getenv("TOKEN")
    or os.getenv("TELEGRAM_TOKEN")
)

if not TOKEN:
    raise ValueError(
        "Не найден токен бота! Проверьте переменные окружения в Railway."
    )

bot = telebot.TeleBot(TOKEN)

# Хранилище состояний для пользователей (для пошаговых вычислений)
user_states = {}
user_data = {}


# Главное меню
def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🎯 Физика")
    btn2 = types.KeyboardButton("🧪 Химия & Вероятности")
    btn3 = types.KeyboardButton("📐 Геометрия")
    markup.add(btn1, btn2)
    markup.add(btn3)
    return markup


# Команда /start
@bot.message_handler(commands=["start"])
def send_welcome(message):
    chat_id = message.chat.id
    user_states.pop(chat_id, None)
    user_data.pop(chat_id, None)

    bot.send_message(
        chat_id,
        "Привет! Я бот для вычислений. Выберите нужный раздел:",
        reply_markup=get_main_keyboard(),
    )


# Обработчик текстовых сообщений и кнопок
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text

    # Кнопка возврата в меню
    if text == "🔙 Назад в меню":
        user_states.pop(chat_id, None)
        user_data.pop(chat_id, None)
        bot.send_message(
            chat_id, "Главное меню:", reply_markup=get_main_keyboard()
        )
        return

    # --- РАЗДЕЛ: ГЕОМЕТРИЯ ---
    if text == "📐 Геометрия":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_vec = types.KeyboardButton("📏 Длина вектора")
        btn_circ = types.KeyboardButton("⭕ Площадь круга")
        btn_back = types.KeyboardButton("🔙 Назад в меню")
        markup.add(btn_vec, btn_circ)
        markup.add(btn_back)
        bot.send_message(
            chat_id, "Геометрия: выберите формулу:", reply_markup=markup
        )
        return

    elif text == "📏 Длина вектора":
        user_states[chat_id] = "waiting_vector"
        bot.send_message(
            chat_id,
            "Введите координаты через пробел или запятую (например: `3 4` или `x1, y1, x2, y2`):",
            parse_mode="Markdown",
        )
        return

    elif text == "⭕ Площадь круга":
        user_states[chat_id] = "waiting_circle_radius"
        bot.send_message(chat_id, "Введите радиус круга (число):")
        return

    # --- РАЗДЕЛ: ФИЗИКА ---
    elif text == "🎯 Физика":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_speed = types.KeyboardButton("🚗 Скорость (S / t)")
        btn_energy = types.KeyboardButton("⚡ Кинетическая энергия (mv²/2)")
        btn_back = types.KeyboardButton("🔙 Назад в меню")
        markup.add(btn_speed, btn_energy)
        markup.add(btn_back)
        bot.send_message(
            chat_id, "Физика: выберите формулу:", reply_markup=markup
        )
        return

    elif text == "🚗 Скорость (S / t)":
        user_states[chat_id] = "waiting_speed_s"
        bot.send_message(chat_id, "Введите расстояние (S в метрах или км):")
        return

    elif text == "⚡ Кинетическая энергия (mv²/2)":
        user_states[chat_id] = "waiting_energy_m"
        bot.send_message(chat_id, "Введите массу тела (m в кг):")
        return

    # --- РАЗДЕЛ: ХИМИЯ & ВЕРОЯТНОСТИ ---
    elif text == "🧪 Химия & Вероятности":
        markup =types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_molar = types.KeyboardButton("⚖️ Молярная масса вещества")
        btn_prob = types.KeyboardButton("🎲 Вероятность события (m / n)")
        btn_back = types.KeyboardButton("🔙 Назад в меню")
        markup.add(btn_molar, btn_prob)
        markup.add(btn_back)
        bot.send_message(
            chat_id, "Химия и Вероятности: выберите расчет:", reply_markup=markup
        )
        return

    elif text == "🎲 Вероятность события (m / n)":
        user_states[chat_id] = "waiting_prob_m"
        bot.send_message(
            chat_id, "Введите количество благоприятных исходов (m):"
        )
        return

    # --- ОБРАБОТКА ВВОДА ДАННЫХ ОТ ПОЛЬЗОВАТЕЛЯ ---
    if chat_id in user_states:
        state = user_states[chat_id]

        # 1. Площадь круга
        if state == "waiting_circle_radius":
            try:
                radius = float(text.replace(",", "."))
                if radius < 0:
                    bot.send_message(
                        chat_id, "Радиус не может быть отрицательным!"
                    )
                    return
                area = math.pi * (radius**2)
                bot.send_message(chat_id, f"📐 Результат: {area:.2f}")
                user_states.pop(chat_id, None)
            except ValueError:
                bot.send_message(chat_id, "Пожалуйста, введите число.")

        # 2. Длина вектора
        elif state == "waiting_vector":
            try:
                cleaned = text.replace(",", " ").replace(";", " ").split()
                numbers = [float(x) for x in cleaned]
                if len(numbers) == 2:
                    length = math.sqrt(numbers[0] ** 2 + numbers[1] ** 2)
                    bot.send_message(chat_id, f"📐 Результат: {length}")
                    user_states.pop(chat_id, None)
                elif len(numbers) == 4:
                    x1, y1, x2, y2 = numbers
                    length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                    bot.send_message(chat_id, f"📐 Результат: {length}")
                    user_states.pop(chat_id, None)
                else:
                    bot.send_message(
                        chat_id,
                        "Введите 2 числа (для координат) или 4 (для отрезка).",
                    )
            except ValueError:
                bot.send_message(
                    chat_id, "Ошибка. Введите числа через пробел."
                )

        # 3. Скорость (Шаг 1: S, Шаг 2: t)
        elif state == "waiting_speed_s":
            try:
                s = float(text.replace(",", "."))
                user_data[chat_id] = {"s": s}
                user_states[chat_id] = "waiting_speed_t"
                bot.send_message(chat_id, "Введите время (t в секундах или часах):")
            except ValueError:
                bot.send_message(chat_id, "Введите корректное число для расстояния.")

        elif state == "waiting_speed_t":
            try:
                t = float(text.replace(",", "."))
                if t == 0:
                    bot.send_message(chat_id, "Время не может быть равно нулю!")
                    return
                s = user_data[chat_id]["s"]
                speed = s / t
                bot.send_message(chat_id, f"🎯 Результат (Скорость): {speed:.2f}")
                user_states.pop(chat_id, None)
                user_data.pop(chat_id, None)
            except ValueError:
                bot.send_message(chat_id, "Введите корректное число для времени.")

        # 4. Кинетическая энергия (Шаг 1: m, Шаг 2: v)
        elif state == "waiting_energy_m":
            try:
                m = float(text.replace(",", "."))
                user_data[chat_id] = {"m": m}
                user_states[chat_id] = "waiting_energy_v"
                bot.send_message(chat_id, "Введите скорость (v в м/с):")
            except ValueError:
                bot.send_message(chat_id, "Введите корректное число для массы.")

        elif state == "waiting_energy_v":
            try:
                v = float(text.replace(",", "."))
                m = user_data[chat_id]["m"]
                energy = (m * (v**2)) / 2
                bot.send_message(
                    chat_id, f"🎯 Результат (Кинетическая энергия): {energy:.2f} Дж"
                )
                user_states.pop(chat_id, None)
                user_data.pop(chat_id, None)
            except ValueError:
                bot.send_message(chat_id, "Введите корректное число для скорости.")

        # 5. Вероятность (Шаг 1: m, Шаг 2: n)
        elif state == "waiting_prob_m":
            try:
                m = float(text.replace(",", "."))
                user_data[chat_id] = {"m": m}
                user_states[chat_id] = "waiting_prob_n"
                bot.send_message(
                    chat_id, "Введите общее количество возможных исходов (n):"
                )
            except ValueError:
                bot.send_message(chat_id, "Введите корректное число.")

        elif state == "waiting_prob_n":
            try:
                n = float(text.replace(",", "."))
                if n == 0:
                    bot.send_message(
                        chat_id, "Общее число исходов (n) не может быть нулем!"
                    )
                    return
                m = user_data[chat_id]["m"]
                prob = m / n
                bot.send_message(
                    chat_id,
                    f"🧪 Результат (Вероятность): {prob:.4f} (или {prob * 100:.2f}%)",
                )
                user_states.pop(chat_id, None)
                user_data.pop(chat_id, None)
            except ValueError:
                bot.send_message(chat_id, "Введите корректное число.")
    else:
        bot.send_message(
            chat_id,
            "Используйте кнопки меню или отправьте /start для перезапуска.",
            reply_markup=get_main_keyboard(),
        )


if __name__ == "__main__":
    print("QuinticSolverBot запущен...")
    bot.infinity_polling()
