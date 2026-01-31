from aiogram import types

# ❌ НЕ загружаем modules здесь!
# Переменная modules будет передана через замыкание или использована из bot.py
# Но так как мы используем кнопки — просто не трогаем modules напрямую

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


async def show_theory_menu(message: types.Message):
    text = "📘 Выберите тему для изучения теории:"
    # Кнопки тем будут сгенерированы в bot.py, но так как мы вызываем отсюда —
    # нам нужно получить список тем. Лучше генерировать меню в bot.py.
    # Но для простоты — оставим как есть, и передадим modules позже.
    # ВРЕМЕННОЕ РЕШЕНИЕ: не используем modules в этом файле.
    # Вместо этого — перенесём логику выбора тем в bot.py.
    
    # Поэтому пока просто покажем словарь и назад
    keyboard = [
        [types.KeyboardButton(text="📖 Словарь терминов")],
        [types.KeyboardButton(text="⬅️ Назад")]
    ]
    reply_markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    await message.answer(text, reply_markup=reply_markup)


async def show_practice_menu(message: types.Message):
    text = "🧩 Выберите тему для решения кейса:"
    keyboard = [
        [types.KeyboardButton(text="🎲 Случайный кейс")],
        [types.KeyboardButton(text="📝 Тест по всем темам")],
        [types.KeyboardButton(text="⬅️ Назад")]
    ]
    reply_markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    await message.answer(text, reply_markup=reply_markup)


async def show_profile(message: types.Message):
    from database.db import get_user_profile
    
    profile = get_user_profile(message.from_user.id)
    if not profile:
        await message.answer("Сначала напишите /start.")
        return

    role_text = "🛡️ Адвокат" if profile["role"] == "defender" else "⚖️ Прокурор"
    
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
        
        f"🛡️ <b>Как адвокат</b>\n"
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