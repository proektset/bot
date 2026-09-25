import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

KEP_BUILD, KEP_APT = range(2)

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Правила группы", callback_data="rules")],
        [InlineKeyboardButton("Эффективность", callback_data="eff")],
        [InlineKeyboardButton("Проектирование", callback_data="design")],
    ])

def back_menu(target="home"):
    return InlineKeyboardMarkup([[InlineKeyboardButton("← Назад", callback_data=target)]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # In groups keep interaction compact; detailed scenarios continue in private chat.
    text = (
        "ПРОЕКТСЕТЬ\n\n"
        "Профессиональное сообщество проектировщиков. "
        "Обмениваемся решениями, проверяем гипотезы и повышаем эффективность проектов."
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=main_menu())
    else:
        q = update.callback_query
        await q.answer()
        await q.edit_message_text(text, reply_markup=main_menu())

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    key = q.data

    if key == "home":
        return await start(update, context)

    if key == "rules":
        text = (
            "ПРАВИЛА ГРУППЫ\n\n"
            "1. Предметно обсуждаем проектирование и инженерные решения.\n"
            "2. Уважаем коллег и аргументируем технические позиции.\n"
            "3. Для вопросов даём исходные данные, ограничения и ожидаемый результат.\n"
            "4. Материалы и решения могут иметь статус: «предложение», «на проверке», «проверено».\n"
            "5. Статус «проверено» присваивается только после проверки ответственным специалистом."
        )
        await q.edit_message_text(text, reply_markup=back_menu())
    elif key == "eff":
        kb = [
            [InlineKeyboardButton("Что такое КЭП?", callback_data="kep_info")],
            [InlineKeyboardButton("Рассчитать КЭП", callback_data="kep_calc")],
            [InlineKeyboardButton("Проверить проект", callback_data="check_project")],
            [InlineKeyboardButton("Как повысить эффективность", callback_data="improve")],
            [InlineKeyboardButton("Исследования и практика", callback_data="research")],
            [InlineKeyboardButton("← Назад", callback_data="home")],
        ]
        await q.edit_message_text("ЭФФЕКТИВНОСТЬ ПРОЕКТА", reply_markup=InlineKeyboardMarkup(kb))
    elif key == "design":
        kb = [
            [InlineKeyboardButton("Задать вопрос", callback_data="ask")],
            [InlineKeyboardButton("Обсудить решение", callback_data="discuss")],
            [InlineKeyboardButton("Найти специалиста", callback_data="specialist")],
            [InlineKeyboardButton("Предложить материал", callback_data="material")],
            [InlineKeyboardButton("← Назад", callback_data="home")],
        ]
        await q.edit_message_text("ПРОЕКТИРОВАНИЕ", reply_markup=InlineKeyboardMarkup(kb))
    elif key == "kep_info":
        await q.edit_message_text(
            "КЭП — коэффициент эффективности планировочного решения.\n\n"
            "КЭП = площадь квартир с лоджиями / строительная площадь этажа.\n\n"
            "Строительная площадь принимается по наружной грани ограждающих конструкций "
            "(кирпичной кладки), с исключением лифтовых шахт и балконов.\n\n"
            "Для корректного сравнения проектов должна применяться единая методика подсчёта.",
            reply_markup=back_menu("eff"),
        )
    elif key in {"check_project","improve","research","ask","discuss","specialist","material"}:
        await q.edit_message_text(
            "Раздел подготовлен к развитию. Функция будет добавлена в следующей версии.",
            reply_markup=back_menu("eff" if key in {"check_project","improve","research"} else "design"),
        )

async def kep_begin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(
        "РАСЧЁТ КЭП\n\nВведите строительную площадь типового этажа, м²:",
        reply_markup=back_menu("eff"),
    )
    return KEP_BUILD

async def kep_build(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        value = float(update.message.text.replace(",", "."))
        if value <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Введите положительное число, например: 820.5")
        return KEP_BUILD
    context.user_data["build_area"] = value
    await update.message.reply_text("Введите площадь квартир с лоджиями, м²:")
    return KEP_APT

async def kep_apt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        apt = float(update.message.text.replace(",", "."))
        if apt <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Введите положительное число.")
        return KEP_APT

    build = context.user_data["build_area"]
    if apt > build:
        await update.message.reply_text("Площадь квартир не должна превышать строительную площадь. Проверьте ввод.")
        return KEP_APT

    kep = apt / build
    await update.message.reply_text(
        f"Результат\n\nСтроительная площадь: {build:.1f} м²\n"
        f"Площадь квартир: {apt:.1f} м²\n"
        f"КЭП: {kep:.3f} ({kep*100:.1f}%)\n\n"
        "Расчёт является предварительной оценкой. Для сравнения проектов используйте единую методику подсчёта площадей.",
        reply_markup=back_menu("eff"),
    )
    context.user_data.clear()
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ПРОЕКТСЕТЬ — бот профессионального сообщества.\n\n"
        "Команды:\n/start — открыть меню\n/help — помощь\n/kep — расчёт КЭП"
    )

async def kep_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Откройте /start → Эффективность → Рассчитать КЭП."
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"Telegram bot error: {context.error!r}")

def run():
    if not TOKEN:
        raise RuntimeError("Не задан TELEGRAM_BOT_TOKEN")
    app = Application.builder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(kep_begin, pattern="^kep_calc$")],
        states={
            KEP_BUILD: [MessageHandler(filters.TEXT & ~filters.COMMAND, kep_build)],
            KEP_APT: [MessageHandler(filters.TEXT & ~filters.COMMAND, kep_apt)],
        },
        fallbacks=[CommandHandler("start", start)],
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("kep", kep_command))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(menu))
    app.add_error_handler(error_handler)
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    run()
