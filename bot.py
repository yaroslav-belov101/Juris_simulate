from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import BOT_TOKEN
from database.db import init_db, ensure_user, get_user_profile
import json
import os
import random

# === ИНИЦИАЛИЗАЦИЯ ===
init_db()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Загружаем модули один раз
with open(os.path.join("data", "modules.json"), "r", encoding="utf-8") as f:
    modules = json.load(f)

user_sessions = {}

# === КОМАНДЫ ===
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = message.from_user
    user_id = user.id
    
    # Создаём пользователя с ролью по умолчанию
    ensure_user(
        user_id=user_id,
        username=user.username or "",
        full_name=f"{user.first_name or ''} {user.last_name or ''}".strip() or "Аноним",
        role="defender"  # по умолчанию — защитник
    )
    
    welcome_text = (
        "🎓 <b>Добро пожаловать в Юридический симулятор!</b>\n\n"
        "Здесь вы научитесь анализировать правовые ситуации с двух точек зрения:\n"
        "• 🛡️ <b>Защитник</b> — защищает права гражданина\n"
        "• ⚖️ <b>Прокурор</b> — выявляет нарушения закона\n\n"
        "👉 Ваша роль по умолчанию: <b>🛡️ Защитник</b>.\n"
        "Вы можете сменить её в разделе <b>👤 Профиль</b>."
    )
    await message.answer(welcome_text, parse_mode="HTML")
    await show_main_menu(message)


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    text = (
        "🎓 <b>Юридический симулятор: Защитник vs Прокурор</b>\n\n"
        "Этот бот помогает понять, что право — это не просто правила, а <b>аргументация и позиция</b>.\n\n"
        "🔹 <b>🛡️ Защитник</b> — защищает права гражданина.\n"
        "🔹 <b>⚖️ Прокурор</b> — выявляет нарушения закона.\n\n"
        "<b>Как пользоваться:</b>\n"
        "1. Нажмите /start\n"
        "2. Перейдите в «📚 Теория» или «🧪 Практика»\n"
        "3. Решайте кейсы и следите за прогрессом\n"
        "4. Смените роль в «👤 Профиль»\n\n"
        "💡 Совет: попробуйте пройти один кейс в обеих ролях — вы увидите разницу!\n\n"
        "Все данные хранятся локально на вашем устройстве."
    )
    await message.answer(text, parse_mode="HTML")


@dp.message(Command("about"))
async def cmd_about(message: types.Message):
    text = (
        "ℹ️ <b>О проекте</b>\n\n"
        "<b>Название:</b> Юридический симулятор\n"
        "<b>Цель:</b> Повысить правовую грамотность школьников через интерактивное обучение.\n\n"
        "<b>Особенности:</b>\n"
        "• Две юридические роли: защитник и прокурор\n"
        "• Реальные кейсы из жизни\n"
        "• Ссылки на статьи законов (ТК РФ, КоАП РФ, ЗоЗПП)\n"
        "• Персональная статистика\n"
        "• Полностью локальное хранение данных\n\n"
        "<b>Технологии:</b>\n"
        "Python 3.12 • aiogram 3 • SQLite • JSON\n\n"
        "© Школьный проект, 2026"
    )
    await message.answer(text, parse_mode="HTML")


# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===
async def show_main_menu(message: types.Message):
    text = "Выберите, что хотите сделать:"
    keyboard = [
        [types.KeyboardButton(text="📚 Теория")],
        [types.KeyboardButton(text="🧪 Практика")],
        [types.KeyboardButton(text="👤 Профиль")]
    ]
    reply_markup = types.ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )
    await message.answer(text, reply_markup=reply_markup)


# === ОСНОВНОЙ ОБРАБОТЧИК ===
@dp.message()
async def handle_messages(message: types.Message):
    user = message.from_user
    user_id = user.id
    text = message.text.strip()

    # Обновляем информацию о пользователе
    ensure_user(
        user_id=user_id,
        username=user.username or "",
        full_name=f"{user.first_name or ''} {user.last_name or ''}".strip() or "Аноним"
    )

    # === Смена роли (обрабатывается в профиле) ===
    if text == "🔄 Сменить роль":
        from database.db import get_user_role, update_user_role
        current_role = get_user_role(user_id)
        new_role = "prosecutor" if current_role == "defender" else "defender"
        update_user_role(user_id, new_role)
        role_text = "⚖️ Прокурор" if new_role == "prosecutor" else "🛡️ Защитник"
        await message.answer(f"✅ Ваша роль изменена на: {role_text}")
        await show_profile(message)
        return

    # === Навигация ===
    if text == "⬅️ Назад":
        await show_main_menu(message)
        user_sessions.pop(user_id, None)
        return

    if text == "👤 Профиль":
        await show_profile(message)
        return

    # === Меню ТЕОРИИ ===
    if text == "📚 Теория":
        from database.db import get_user_role
        user_sessions[user_id] = {"mode": "theory"}
        msg_text = "📘 Выберите тему для изучения теории:"
        keyboard = [[types.KeyboardButton(text=m["title"])] for m in modules]
        keyboard.append([types.KeyboardButton(text="📖 Словарь терминов")])
        keyboard.append([types.KeyboardButton(text="⬅️ Назад")])
        reply_markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        await message.answer(msg_text, reply_markup=reply_markup)
        return

    # === Меню ПРАКТИКИ ===
    if text == "🧪 Практика":
        from database.db import get_user_role
        user_sessions[user_id] = {"mode": "practice"}
        msg_text = "🧩 Выберите тему для решения кейса:"
        keyboard = [[types.KeyboardButton(text=m["title"])] for m in modules]
        keyboard.append([types.KeyboardButton(text="🎲 Случайный кейс")])
        keyboard.append([types.KeyboardButton(text="📝 Тест по всем темам")])
        keyboard.append([types.KeyboardButton(text="⬅️ Назад")])
        reply_markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        await message.answer(msg_text, reply_markup=reply_markup)
        return

    # === Словарь терминов ===
    if text == "📖 Словарь терминов":
        terms_text = (
            "📖 <b>Юридический словарь</b>\n\n"
            "<b>ГК РФ</b> — Гражданский кодекс Российской Федерации. Регулирует имущественные и личные неимущественные отношения.\n\n"
            "<b>ТК РФ</b> — Трудовой кодекс РФ. Регулирует трудовые отношения.\n\n"
            "<b>КоАП РФ</b> — Кодекс об административных правонарушениях. Штрафы за нарушения (не уголовные).\n\n"
            "<b>УК РФ</b> — Уголовный кодекс РФ. Самые серьёзные преступления.\n\n"
            "<b>ЗоЗПП</b> — Закон РФ «О защите прав потребителей». Защищает покупателей.\n\n"
            "<b>Исковая давность</b> — Срок, в течение которого можно подать в суд (обычно 3 года).\n\n"
            "<b>Административная ответственность</b> — Ответственность за правонарушения, выражающаяся в штрафах, предупреждениях."
        )
        keyboard = [[types.KeyboardButton(text="⬅️ Назад")]]
        reply_markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        await message.answer(terms_text, parse_mode="HTML", reply_markup=reply_markup)
        return

    # === Случайный кейс ===
    if text == "🎲 Случайный кейс":
        from database.db import get_user_role
        role = get_user_role(user_id)
        all_cases = []
        all_modules = []
        for module in modules:
            if role in module["roles"] and "cases" in module["roles"][role]:
                cases = module["roles"][role]["cases"]
                for case in cases:
                    all_cases.append(case)
                    all_modules.append(module)
        
        if not all_cases:
            await message.answer("Нет доступных кейсов.")
            return

        idx = random.randint(0, len(all_cases) - 1)
        case = all_cases[idx]
        module = all_modules[idx]

        user_sessions[user_id] = {
            "mode": "answering",
            "case": case,
            "role": role,
            "module_title": module["title"]
        }

        question_text = (
            f"🎲 <b>Случайный кейс</b>\n\n"
            f"<b>Тема:</b> {module['title']}\n"
            f"<b>Роль:</b> {'🛡️ Защитник' if role == 'defender' else '⚖️ Прокурор'}\n\n"
            f"<b>Ситуация:</b>\n{module['situation']}\n\n"
            f"<b>Ваша цель:</b> {case['goal']}"
        )
        options = case["options"]
        keyboard = [[types.KeyboardButton(text=opt)] for opt in options]
        keyboard.append([types.KeyboardButton(text="⬅️ Назад")])
        reply_markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        await message.answer(question_text, parse_mode="HTML", reply_markup=reply_markup)
        return

    # === Тест по всем темам ===
    if text == "📝 Тест по всем темам":
        from database.db import get_user_role
        role = get_user_role(user_id)
        all_cases = []
        all_modules = []
        for module in modules:
            if role in module["roles"] and "cases" in module["roles"][role]:
                cases = module["roles"][role]["cases"]
                for case in cases:
                    all_cases.append(case)
                    all_modules.append(module)
        
        if not all_cases:
            await message.answer("Нет доступных кейсов для теста.")
            return

        test_size = min(5, len(all_cases))
        selected_indices = random.sample(range(len(all_cases)), test_size)
        quiz_cases = [all_cases[i] for i in selected_indices]
        quiz_modules = [all_modules[i] for i in selected_indices]
        
        user_sessions[user_id] = {
            "mode": "quiz",
            "quiz_cases": quiz_cases,
            "quiz_modules": quiz_modules,
            "quiz_index": 0,
            "quiz_correct": 0,
            "role": role
        }
        await send_quiz_question(message)
        return

    # === Выбор темы ===
    module_titles = [m["title"] for m in modules]
    if text in module_titles:
        module = next(m for m in modules if m["title"] == text)
        session = user_sessions.get(user_id)
        if not session:
            await show_main_menu(message)
            return

        from database.db import get_user_role
        role = get_user_role(user_id)

        if session["mode"] == "theory":
            theory_text = module["roles"][role]["theory"]
            keyboard = [[types.KeyboardButton(text="⬅️ Назад")]]
            reply_markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
            await message.answer(theory_text, parse_mode="HTML", reply_markup=reply_markup)
            return

        elif session["mode"] == "practice":
            cases = module["roles"][role]["cases"]
            case = random.choice(cases)
            user_sessions[user_id] = {
                "mode": "answering",
                "case": case,
                "role": role,
                "module_title": module["title"]
            }

            question_text = (
                f"🧩 <b>Кейс: {module['title']}</b>\n\n"
                f"<b>Ваша цель:</b> {case['goal']}\n\n"
                f"<b>Ситуация:</b>\n{module['situation']}"
            )
            options = case["options"]
            keyboard = [[types.KeyboardButton(text=opt)] for opt in options]
            keyboard.append([types.KeyboardButton(text="⬅️ Назад")])
            reply_markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
            await message.answer(question_text, parse_mode="HTML", reply_markup=reply_markup)
            return

    # === Обработка ответов ===
    session = user_sessions.get(user_id)
    if session:
        if session.get("mode") == "answering":
            case = session["case"]
            role = session["role"]
            correct_options = [case["options"][i] for i in case["correct_indices"]]
            is_correct = text in correct_options
            
            from database.db import update_user_stats
            update_user_stats(user_id, is_correct, role)

            if is_correct:
                feedback = "✅ Правильно! " + case["explanation"]
            else:
                feedback = "❌ Почти! Правильные ответы:\n\n" + "\n".join(f"• {opt}" for opt in correct_options) + "\n\n" + case["explanation"]

            profile = get_user_profile(user_id)
            total = profile["total"]
            correct = profile["correct"]
            percent = round(correct / total * 100) if total > 0 else 0
            feedback += f"\n\n📊 Общий прогресс: {correct}/{total} ({percent}%)"

            keyboard = [[types.KeyboardButton(text="⬅️ Назад")]]
            reply_markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
            await message.answer(feedback, parse_mode="HTML", reply_markup=reply_markup)
            user_sessions.pop(user_id, None)
            return

        elif session.get("mode") == "quiz":
            idx = session["quiz_index"]
            case = session["quiz_cases"][idx]
            correct_options = [case["options"][i] for i in case["correct_indices"]]
            is_correct = text in correct_options

            if is_correct:
                session["quiz_correct"] += 1

            session["quiz_index"] += 1
            await send_quiz_question(message)
            return

    # Неизвестное сообщение
    await message.answer(
        "Не понял команду. Нажмите «⬅️ Назад» или используйте меню.",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text="⬅️ Назад")]],
            resize_keyboard=True
        )
    )


# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===
async def send_quiz_question(message: types.Message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id)
    if not session or session["quiz_index"] >= len(session["quiz_cases"]):
        correct = session["quiz_correct"]
        total = len(session["quiz_cases"])
        percent = round(correct / total * 100)
        result_text = (
            f"🎉 <b>Тест завершён!</b>\n\n"
            f"Правильно: {correct} из {total}\n"
            f"Процент: {percent}%\n\n"
        )
        if percent >= 80:
            result_text += "🏆 Отлично! Вы отлично разбираетесь в праве!"
        elif percent >= 60:
            result_text += "👍 Хорошо! Есть что повторить."
        else:
            result_text += "📚 Советуем повторить темы."

        keyboard = [[types.KeyboardButton(text="⬅️ Назад")]]
        reply_markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        await message.answer(result_text, parse_mode="HTML", reply_markup=reply_markup)
        user_sessions.pop(user_id, None)
        return

    idx = session["quiz_index"]
    case = session["quiz_cases"][idx]
    module = session["quiz_modules"][idx]

    question_text = (
        f"📝 <b>Вопрос {idx + 1} из {len(session['quiz_cases'])}</b>\n\n"
        f"<b>Тема:</b> {module['title']}\n"
        f"<b>Ситуация:</b>\n{module['situation']}\n\n"
        f"<b>Ваша цель:</b> {case['goal']}"
    )
    options = case["options"]
    keyboard = [[types.KeyboardButton(text=opt)] for opt in options]
    reply_markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    await message.answer(question_text, parse_mode="HTML", reply_markup=reply_markup)


async def show_profile(message: types.Message):
    profile = get_user_profile(message.from_user.id)
    if not profile:
        await message.answer("Сначала напишите /start.")
        return

    role_text = "🛡️ Защитник" if profile["role"] == "defender" else "⚖️ Прокурор"
    
    name = profile["full_name"] or "Не указано"
    username = f"@{profile['username']}" if profile["username"] else "—"
    
    total = profile["total"]
    correct = profile["correct"]
    overall_percent = round(correct / total * 100) if total > 0 else 0

    def_total = profile["defender_total"]
    def_correct = profile["defender_correct"]
    def_percent = round(def_correct / def_total * 100) if def_total > 0 else 0

    proc_total = profile["prosecutor_total"]
    proc_correct = profile["prosecutor_correct"]
    proc_percent = round(proc_correct / proc_total * 100) if proc_total > 0 else 0

    from datetime import datetime
    try:
        first = datetime.fromisoformat(profile["first_seen"]).strftime("%d.%m.%Y")
        last = datetime.fromisoformat(profile["last_seen"]).strftime("%d.%m.%Y")
    except:
        first = last = "—"

    text = (
        f"👤 <b>Ваш профиль</b>\n\n"
        f"Имя: {name}\n"
        f"Username: {username}\n"
        f"Текущая роль: {role_text}\n\n"
        
        f"📊 <b>Общая статистика</b>\n"
        f"Всего кейсов: {total}\n"
        f"Правильно: {correct} ({overall_percent}%)\n\n"
        
        f"🛡️ <b>Как защитник</b>\n"
        f"Кейсов: {def_total} | Правильно: {def_correct} ({def_percent}%)\n\n"
        
        f"⚖️ <b>Как прокурор</b>\n"
        f"Кейсов: {proc_total} | Правильно: {proc_correct} ({proc_percent}%)\n\n"
        
        f"📅 Первое обращение: {first}\n"
        f"Последнее: {last}"
    )
    
    keyboard = [
        [types.KeyboardButton(text="🔄 Сменить роль")],
        [types.KeyboardButton(text="⬅️ Назад")]
    ]
    reply_markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    await message.answer(text, parse_mode="HTML", reply_markup=reply_markup)


# === ЗАПУСК ===
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())