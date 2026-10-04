import json
import math
import os
import time
import urllib.parse
import urllib.request

TOKEN = "8812405036:AAFbA1CviM7VOTyXclhtbVsKHtsFEn4YD_M"
URL = f"https://api.telegram.org/bot{TOKEN}/"
DOWNLOAD_DIR = "/storage/emulated/0/Download/"

# База данных формул с описаниями и синтаксисом
FORMULAS_DB = {
    "algebra_quad": {
        "title": "🧮 Квадратные уравнения",
        "desc": (
            "**Формула:** ax² + bx + c = 0\n"
            "• Дискриминант: D = b² - 4ac\n"
            "• Корни: x₁,₂ = (-b ± √D) / (2a)\n\n"
            "**Как использовать:**\nОтправьте коэффициенты через запятую:"
            " `1, -5, 6`"
        ),
    },
    "algebra_sys": {
        "title": "📈 Системы линейных уравнений",
        "desc": (
            "**Формула:**\n"
            "a₁x + b₁y = c₁\n"
            "a₂x + b₂y = c₂\n\n"
            "**Как использовать:**\n`linear_sys(a1, b1, c1, a2, b2, c2)`\nПример:"
            " `linear_sys(2, 1, 5, 1, -1, 1)`"
        ),
    },
    "algebra_arith": {
        "title": "📉 Арифметическая прогрессия",
        "desc": (
            "**Формулы:**\n"
            "• n-й член: an = a₁ + d(n-1)\n"
            "• Сумма: Sn = ((2a₁ + d(n-1)) / 2) * n\n\n"
            "**Как использовать:**\n`arith_prog(a1, d, n)`\nПример:"
            " `arith_prog(2, 3, 5)`"
        ),
    },
    "geom_vec": {
        "title": "📏 Длина вектора",
        "desc": (
            "**Формула:** |a| = √(x² + y²)\n\n**Как использовать:**\n`vec_len(x,"
            " y)`\nПример: `vec_len(5, 12)`"
        ),
    },
    "geom_circle": {
        "title": "⭕ Площадь круга",
        "desc": (
            "**Формула:** S = πr²\n\n**Как использовать:**\n`circle_area(r)`\nПример:"
            " `circle_area(4)`"
        ),
    },
    "phys_bullet": {
        "title": "🎯 Баллистика полета",
        "desc": (
            "**Описание:** Расчет времени, максимальной высоты и дальности"
            " полета тела.\n\n**Как использовать:**\n`bullet_flight(v0,"
            " angle)`\n• `v0` — скорость (м/с)\n• `angle` — угол (°)\nПример:"
            " `bullet_flight(100, 45)`"
        ),
    },
    "phys_ohm": {
        "title": "⚡ Закон Ома (Напряжение)",
        "desc": (
            "**Формула:** U = I * R\n• U — напряжение (В)\n• I — ток (А)\n• R —"
            " сопротивление (Ом)\n\n**Как использовать:**\n`ohm_u(current,"
            " resistance)`\nПример: `ohm_u(2, 15)`"
        ),
    },
    "phys_energy": {
        "title": "💥 Кинетическая энергия",
        "desc": (
            "**Формула:** Ek = (m * v²) / 2\n• m — масса (кг)\n• v — скорость"
            " (м/с)\n\n**Как использовать:**\n`kinetic_energy(mass,"
            " velocity)`\nПример: `kinetic_energy(2, 10)`"
        ),
    },
    "chem_moles": {
        "title": "🧪 Количество вещества (Моли)",
        "desc": (
            "**Формула:** ν = m / M\n• m — масса (г)\n• M — молярная масса"
            " (г/моль)\n\n**Как использовать:**\n`moles(mass, molar_mass)`\nПример:"
            " `moles(18, 18)`"
        ),
    },
    "prob_calc": {
        "title": "🎲 Теория вероятностей",
        "desc": (
            "**Формула:** P = m / n\n• m — благоприятные исходы\n• n — всего"
            " исходов\n\n**Как использовать:**\n`probability(m_fav,"
            " n_tot)`\nПример: `probability(2, 36)`"
        ),
    },
}


def send_message(chat_id, text, reply_markup=None):
  data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
  if reply_markup:
    data["reply_markup"] = json.dumps(reply_markup)
  encoded_data = urllib.parse.urlencode(data).encode("utf-8")
  req = urllib.request.Request(
      URL + "sendMessage",
      data=encoded_data,
      headers={"User-Agent": "Mozilla/5.0"},
  )
  try:
    urllib.request.urlopen(req, timeout=10)
  except Exception as e:
    print(f"Ошибка отправки: {e}")


def answer_callback_query(callback_query_id):
  data = {"callback_query_id": callback_query_id}
  encoded_data = urllib.parse.urlencode(data).encode("utf-8")
  req = urllib.request.Request(
      URL + "answerCallbackQuery",
      data=encoded_data,
      headers={"User-Agent": "Mozilla/5.0"},
  )
  try:
    urllib.request.urlopen(req, timeout=5)
  except Exception:
    pass


def get_updates(offset=None):
  url = URL + "getUpdates?timeout=20"
  if offset:
    url += f"&offset={offset}"
  req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
  try:
    response = urllib.request.urlopen(req, timeout=25)
    return json.loads(response.read().decode("utf-8"))
  except Exception as e:
    print(f"⚠️ Сбой сети (переподключение...): {e}")
    time.sleep(3)
    return {"result": []}


def download_telegram_file(file_id, save_path):
  try:
    info_url = f"{URL}getFile?file_id={file_id}"
    req = urllib.request.Request(info_url, headers={"User-Agent": "Mozilla/5.0"})
    file_info = json.loads(
        urllib.request.urlopen(req, timeout=10).read().decode("utf-8")
    )
    if file_info.get("ok"):
      file_path = file_info["result"]["file_path"]
      download_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
      urllib.request.urlretrieve(download_url, save_path)
      return True
  except Exception as e:
    print(f"Ошибка скачивания файла: {e}")
  return False


# Интерактивные меню
def get_main_menu_keyboard():
  return {
      "inline_keyboard": [
          [{"text": "📐 Алгебра", "callback_data": "menu_algebra"}],
          [{"text": "📏 Геометрия", "callback_data": "menu_geometry"}],
          [{"text": "🎯 Физика", "callback_data": "menu_physics"}],
          [{"text": "🧪 Химия", "callback_data": "menu_chemistry"}],
          [{"text": "🎲 Теория вероятностей", "callback_data": "menu_prob"}],
      ]
  }


def get_algebra_keyboard():
  return {
      "inline_keyboard": [
          [{"text": "🧮 Квадратные уравнения", "callback_data": "algebra_quad"}],
          [
              {
                  "text": "📈 Системы линейных уравнений",
                  "callback_data": "algebra_sys",
              }
          ],
          [{"text": "📉 Арифметическая прогрессия", "callback_data": "algebra_arith"}],
          [{"text": "🔙 Назад в меню", "callback_data": "back_to_main"}],
      ]
  }


def get_geometry_keyboard():
  return {
      "inline_keyboard": [
          [{"text": "📏 Длина вектора", "callback_data": "geom_vec"}],
          [{"text": "⭕ Площадь круга", "callback_data": "geom_circle"}],
          [{"text": "🔙 Назад в меню", "callback_data": "back_to_main"}],
      ]
  }


def get_physics_keyboard():
  return {
      "inline_keyboard": [
          [{"text": "🎯 Баллистика полета", "callback_data": "phys_bullet"}],
          [{"text": "⚡ Закон Ома (U)", "callback_data": "phys_ohm"}],
          [{"text": "💥 Кинетическая энергия", "callback_data": "phys_energy"}],
          [{"text": "🔙 Назад в меню", "callback_data": "back_to_main"}],
      ]
  }


def get_chemistry_keyboard():
  return {
      "inline_keyboard": [
          [{"text": "🧪 Количество вещества (Моли)", "callback_data": "chem_moles"}],
          [{"text": "🔙 Назад в меню", "callback_data": "back_to_main"}],
      ]
  }


def get_prob_keyboard():
  return {
      "inline_keyboard": [
          [{"text": "🎲 Расчет вероятности", "callback_data": "prob_calc"}],
          [{"text": "🔙 Назад в меню", "callback_data": "back_to_main"}],
      ]
  }


def solve_math_text(text):
  text_clean = text.strip()

  # Замена юникод-дробей на десятичные эквиваленты
  fraction_map = {
      "¼": "+0.25",
      "½": "+0.5",
      "¾": "+0.75",
      "⅛": "+0.125",
      "⅜": "+0.375",
      "⅝": "+0.625",
      "⅞": "+0.875",
      "⅓": "+0.3333",
      "⅔": "+0.6667",
  }
  for frac, dec in fraction_map.items():
    text_clean = text_clean.replace(frac, dec)

  # Обработка квадратного уравнения через запятую (например: 1, -5, 6)
  if "," in text_clean and "(" not in text_clean:
    try:
      parts = [float(p.strip()) for p in text_clean.replace(";", ",").split(",")]
      if len(parts) == 3:
        a, b, c = parts
        if a == 0:
          return "⚠️ Коэффициент 'a' не может быть равен нулю."
        d = b**2 - 4 * a * c
        if d > 0:
          x1 = (-b + math.sqrt(d)) / (2 * a)
          x2 = (-b - math.sqrt(d)) / (2 * a)
          return (
              f"🧮 **Квадратное уравнение:**\nДискриминант (D) ="
              f" {d}\nКорни:\nx₁ = {x1:.4f}\nx₂ = {x2:.4f}"
          )
        elif d == 0:
          x1 = -b / (2 * a)
          return (
              f"🧮 **Квадратное уравнение:**\nДискриминант (D) = 0\nКорень x ="
              f" {x1:.4f}"
          )
        else:
          return (
              f"🧮 **Квадратное уравнение:**\nДискриминант (D) ="
              f" {d}\nДействительных корней нет (D < 0)."
          )
    except Exception:
      pass

  # Безопасный словарь для расчетов
  safe_dict = {
      "sin": math.sin,
      "cos": math.cos,
      "tan": math.tan,
      "sqrt": math.sqrt,
      "pi": math.pi,
      "e": math.e,
      "log": math.log,
      "pow": pow,
      "factorial": math.factorial,
      "linear_sys": lambda a1, b1, c1, a2, b2, c2: (
          f"📈 **Система линейных уравнений:**\n"
          f"x = { (c1*b2 - c2*b1) / (a1*b2 - a2*b1) if (a1*b2 - a2*b1) != 0 else 'Нет решений' }\n"
          f"y = { (a1*c2 - a2*c1) / (a1*b2 - a2*b1) if (a1*b2 - a2*b1) != 0 else 'Нет решений' }"
      ),
      "arith_prog": lambda a1, d, n: (
          f"📉 **Арифметическая прогрессия:**\n• n-й член (an) ="
          f" {a1 + d * (n - 1)}\n• Сумма (Sn) ="
          f" {((2 * a1 + d * (n - 1)) / 2) * n}"
      ),
      "geom_prog": lambda b1, q, n: (
          f"📈 **Геометрическая прогрессия:**\n• n-й член (bn) ="
          f" {b1 * (q ** (n - 1))}\n• Сумма (Sn) ="
          f" {b1 * ((q**n - 1) / (q - 1)) if q != 1 else b1 * n}"
      ),
      "combinations": math.comb,
      "permutations": math.perm,
      "vec_len": lambda x, y: math.sqrt(x**2 + y**2),
      "circle_area": lambda r: math.pi * r**2,
      "triangle_heron": lambda a, b, c: math.sqrt(
          (p := (a + b + c) / 2) * (p - a) * (p - b) * (p - c)
      ),
      "bullet_flight": lambda v0, angle: (
          f"🎯 **Баллистика пули:**\n• Время полета: {round((2 * v0 * math.sin(math.radians(angle))) / 9.81, 2)} с\n• Макс. высота: {round((v0**2 * (math.sin(math.radians(angle)) ** 2)) / 19.62, 2)} м\n• Дальность: {round((v0**2 * math.sin(math.radians(2 * angle))) / 9.81, 2)} м"
      ),
      "kinematic_s": lambda v0, t, a: v0 * t + (a * t**2) / 2,
      "kinetic_energy": lambda m, v: (m * v**2) / 2,
      "ohm_u": lambda i, r: i * r,
      "ideal_gas_p": lambda nu, t, v: (nu * 8.31 * t) / v,
      "lens_f": lambda d, f_focus: (d * f_focus) / (d - f_focus),
      "moles": lambda m, molar_m: m / molar_m,
      "probability": lambda m_fav, n_tot: m_fav / n_tot,
  }

  try:
    expr = text_clean.replace("^", "**")
    result = eval(expr, {"__builtins__": {}}, safe_dict)
    return f"{result}" if isinstance(result, str) else f"📐 **Результат:** {result}"
  except Exception:
    return (
        "❌ Неизвестная команда или выражение.\n\nНапишите /start, чтобы открыть"
        " интерактивное меню с предметами и формулами."
    )


def main():
  print("QuinticSolverBot (Универсальный и стабильный) запущен...")
  offset = None
  while True:
    updates = get_updates(offset)
    for update in updates.get("result", []):
      offset = update["update_id"] + 1

      if "callback_query" in update:
        cq = update["callback_query"]
        cq_id = cq["id"]
        chat_id = cq["message"]["chat"]["id"]
        data = cq["data"]
        answer_callback_query(cq_id)

        if data == "back_to_main":
          send_message(
              chat_id,
              "🎓 **Главное меню:**\nВыберите интересующий вас предмет:",
              get_main_menu_keyboard(),
          )
        elif data == "menu_algebra":
          send_message(
              chat_id, "📐 **Алгебра:** выберите формулу:", get_algebra_keyboard()
          )
        elif data == "menu_geometry":
          send_message(
              chat_id, "📏 **Геометрия:** выберите формулу:", get_geometry_keyboard()
          )
        elif data == "menu_physics":
          send_message(
              chat_id, "🎯 **Физика:** выберите формулу:", get_physics_keyboard()
          )
        elif data == "menu_chemistry":
          send_message(
              chat_id, "🧪 **Химия:** выберите формулу:", get_chemistry_keyboard()
          )
        elif data == "menu_prob":
          send_message(
              chat_id,
              "🎲 **Теория вероятностей:** выберите формулу:",
              get_prob_keyboard(),
          )
        elif data in FORMULAS_DB:
          formula_info = FORMULAS_DB[data]
          text = f"📌 *{formula_info['title']}*\n\n{formula_info['desc']}"
          send_message(chat_id, text, get_main_menu_keyboard())

      elif "message" in update:
        message = update["message"]
        chat_id = message.get("chat", {}).get("id")
        if not chat_id:
          continue

        if "photo" in message:
          photo_list = message["photo"]
          best_photo = photo_list[-1]
          file_id = best_photo["file_id"]
          save_path = os.path.join(
              DOWNLOAD_DIR, f"task_image_{int(time.time())}.jpg"
          )
          success = download_telegram_file(file_id, save_path)
          if success:
            send_message(
                chat_id,
                "📷 **Фото успешно сохранено в папку Загрузки!**\nТеперь можете"
                " воспользоваться формулами из меню.",
            )
          else:
            send_message(chat_id, "❌ Не удалось сохранить фото.")

        elif "text" in message:
          text = message["text"]
          if text.startswith("/start"):
            send_message(
                chat_id,
                "🎓 Привет! Я **QuinticSolverBot** — твой персональный"
                " помощник.\n\nВыберите нужный предмет в меню ниже, чтобы"
                " посмотреть формулы, или сразу отправьте расчет / фото задачи:",
                get_main_menu_keyboard(),
            )
          else:
            answer = solve_math_text(text)
            send_message(chat_id, answer)

    time.sleep(0.5)


if __name__ == "__main__":
  main()
pyTelegramBotAPI
numpy
matplotlib
requests
