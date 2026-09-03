import json
import logging
import os
import subprocess
from pathlib import Path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN, CHANNELS, CHEATS

import sys

ADMIN_ID = int(os.environ.get("ADMIN_ID", "6367594269"))
USERS_FILE = Path("users.json")
CUSTOM_CHEATS_FILE = Path("custom_cheats.json")
CHEATS_DIR = Path("cheats")

UPLOAD_NAME, UPLOAD_FILE = range(2)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

user_data: dict[int, dict] = {}
broadcast_state: dict[int, bool] = {}


def load_users() -> set[int]:
    if USERS_FILE.exists():
        return set(json.loads(USERS_FILE.read_text(encoding="utf-8")))
    return set()


def save_user(user_id: int) -> None:
    users = load_users()
    users.add(user_id)
    USERS_FILE.write_text(json.dumps(list(users)), encoding="utf-8")
    try:
        token = os.environ.get("GITHUB_TOKEN", "")
        subprocess.run(["git", "config", "user.name", "seimjuzsliv"], capture_output=True, timeout=10)
        subprocess.run(["git", "config", "user.email", "bot@seimjuzsliv.bot"], capture_output=True, timeout=10)
        subprocess.run(["git", "remote", "set-url", "origin", f"https://{token}@github.com/seimuwork-sudo/telegram-bot-cheats.git"], capture_output=True, timeout=10)
        subprocess.run(["git", "add", "users.json"], capture_output=True, timeout=10)
        subprocess.run(["git", "commit", "-m", f"Update users ({len(users)} total)"], capture_output=True, timeout=10)
        subprocess.run(["git", "push"], capture_output=True, timeout=30)
    except Exception as e:
        logger.error("Failed to push users.json: %s", e)


def load_custom_cheats() -> dict:
    if CUSTOM_CHEATS_FILE.exists():
        return json.loads(CUSTOM_CHEATS_FILE.read_text(encoding="utf-8"))
    return {}


def save_custom_cheats(cheats: dict) -> None:
    CUSTOM_CHEATS_FILE.write_text(json.dumps(cheats, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        token = os.environ.get("GITHUB_TOKEN", "")
        subprocess.run(["git", "config", "user.name", "seimjuzsliv"], capture_output=True, timeout=10)
        subprocess.run(["git", "config", "user.email", "bot@seimjuzsliv.bot"], capture_output=True, timeout=10)
        subprocess.run(["git", "remote", "set-url", "origin", f"https://{token}@github.com/seimuwork-sudo/telegram-bot-cheats.git"], capture_output=True, timeout=10)
        subprocess.run(["git", "add", "cheats/", "custom_cheats.json"], capture_output=True, timeout=10)
        subprocess.run(["git", "commit", "-m", f"Add cheat: {list(cheats.values())[-1]['name']}"], capture_output=True, timeout=10)
        subprocess.run(["git", "push"], capture_output=True, timeout=30)
    except Exception as e:
        logger.error("Failed to push custom cheats: %s", e)


def get_all_cheats() -> dict:
    all_cheats = dict(CHEATS)
    all_cheats.update(load_custom_cheats())
    return all_cheats


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    save_user(user.id)
    keyboard = [
        [InlineKeyboardButton("⬇️  Скачать чит", callback_data="download")],
        [InlineKeyboardButton("💎  Наша база читов", callback_data="base")],
        [InlineKeyboardButton("📋  Правила", callback_data="rules")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"👋 *Добро пожаловать,* _{user.first_name}!_\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ *Я бот для выдачи читов*\n"
        "🎮 _Быстро · Безопасно · Надёжно_\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Выбери действие 👇",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    save_user(query.from_user.id)

    all_cheats = get_all_cheats()
    keyboard = []
    emojis = ["🔥", "⚡", "💎", "⭐", "🎮", "🎯", "🚀", "💰"]
    for i, (key, cheat) in enumerate(all_cheats.items()):
        emoji = emojis[i % len(emojis)]
        keyboard.append([InlineKeyboardButton(f"{emoji} {cheat['name']}", callback_data=f"cheat_{key}")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_main")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📦 *ВЫБЕРИ ЧИТ*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Нажми на нужный чит 👇",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def cheat_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    save_user(query.from_user.id)

    user_id = query.from_user.id
    cheat_key = query.data.replace("cheat_", "")
    all_cheats = get_all_cheats()

    if cheat_key not in all_cheats:
        await query.edit_message_text("❌ *Чит не найден.* Нажми /start заново.", parse_mode="Markdown")
        return

    user_data[user_id] = {"cheat": cheat_key}

    keyboard = [
        [InlineKeyboardButton("✅ Принимаю правила", callback_data="accept_rules")],
        [InlineKeyboardButton("❌ Отказаться", callback_data="back_main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎮 *{all_cheats[cheat_key]['name']}*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📋 *ПРАВИЛА ИСПОЛЬЗОВАНИЯ:*\n\n"
        "1️⃣ _Подпишись на все каналы_\n"
        "2️⃣ _Нажми «Проверить подписку»_\n"
        "3️⃣ _Получи файл чита_\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "❗ *ДИСКЛЕЙМЕР*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "_Мы не являемся авторами кряков и не взламываем читы._\n"
        "_Мы берём кряки у проверенных сторонних источников._\n"
        "_Гарантии отсутствия вирусов мы не даём —_ *скачивай на свой страх и риск.*\n"
        "_Скачивая файлы, ты подтверждаешь, что понимаешь это._\n\n"
        "Нажми «Принимаю правила» чтобы продолжить 👇",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def accept_rules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    save_user(query.from_user.id)

    user_id = query.from_user.id
    cheat_key = user_data.get(user_id, {}).get("cheat")
    all_cheats = get_all_cheats()

    if not cheat_key or cheat_key not in all_cheats:
        await query.edit_message_text("❌ *Ошибка.* Нажми /start заново.", parse_mode="Markdown")
        return

    buttons = []
    for i, ch in enumerate(CHANNELS, 1):
        buttons.append(
            [InlineKeyboardButton(
                f"🔗 {i}. {ch['label']}",
                url=f"https://t.me/{ch['username']}",
            )]
        )
    buttons.append([InlineKeyboardButton("✅ ПРОВЕРИТЬ ПОДПИСКУ", callback_data="check_sub")])
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back_main")])

    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎮 *{all_cheats[cheat_key]['name']}*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📢 _Чтобы скачать чит, подпишись на все каналы:_\n\n"
        "Нажми на канал → *Подписаться* → Вернись сюда\n\n"
        "После подписки нажми кнопку ниже 👇",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    save_user(query.from_user.id)

    user_id = query.from_user.id
    all_cheats = get_all_cheats()
    not_subscribed = []

    for ch in CHANNELS:
        try:
            member = await context.bot.get_chat_member(
                chat_id=ch["chat_id"],
                user_id=user_id,
            )
            logger.info("Check %s for user %s: status=%s", ch["username"], user_id, member.status)
            if member.status not in ("member", "administrator", "creator"):
                not_subscribed.append(ch["label"])
        except Exception as e:
            logger.error("Error checking %s: %s", ch["username"], e)
            not_subscribed.append(ch["label"])

    if not_subscribed:
        channels_text = "\n".join(f"  ❌ *{name}*" for name in not_subscribed)
        keyboard = []
        for i, ch in enumerate(CHANNELS, 1):
            keyboard.append(
                [InlineKeyboardButton(
                    f"🔗 {i}. {ch['label']}",
                    url=f"https://t.me/{ch['username']}",
                )]
            )
        keyboard.append([InlineKeyboardButton("✅ ПРОВЕРИТЬ ЕЩЁ РАЗ", callback_data="check_sub")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ *ПРОВЕРКА ПОДПИСКИ*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Ты не подписан на:\n{channels_text}\n\n"
            "_Подпишись и нажми кнопку снова_ 👇",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
        return

    cheat_key = user_data.get(user_id, {}).get("cheat")
    if not cheat_key or cheat_key not in all_cheats:
        await query.edit_message_text("❌ *Ошибка.* Нажми /start заново.", parse_mode="Markdown")
        return

    cheat = all_cheats[cheat_key]
    await query.edit_message_text(
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "✅ *ВСЕ ПОДПИСКИ ПРОВЕРЕНЫ!*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📦 _Отправляю файлы..._",
        parse_mode="Markdown",
    )

    for file_path in cheat["files"]:
        path = Path(file_path)
        if path.exists():
            with open(path, "rb") as f:
                await context.bot.send_document(
                    chat_id=user_id,
                    document=f,
                    filename=path.name,
                )
        else:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"❌ Файл `{path.name}` не найден.",
                parse_mode="Markdown",
            )

    await context.bot.send_message(
        chat_id=user_id,
        text=(
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🎉 *ФАЙЛЫ ОТПРАВЛЕНЫ!*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "⚡ _Удачи в игре!_\n"
            "🛡 _Нужна помощь →_ /start"
        ),
        parse_mode="Markdown",
    )

    del user_data[user_id]


async def base(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    save_user(query.from_user.id)

    all_cheats = get_all_cheats()
    keyboard = [
        [InlineKeyboardButton("⬇️ Скачать", callback_data="download")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    emojis = ["🔥", "⚡", "💎", "⭐", "🎮", "🎯", "🚀", "💰"]
    cheats_text = ""
    for i, (key, cheat) in enumerate(all_cheats.items()):
        emoji = emojis[i % len(emojis)]
        cheats_text += f"{emoji} *{cheat['name']}*\n"

    await query.edit_message_text(
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💎 *НАША БАЗА ЧИТОВ*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{cheats_text}\n"
        "_Все читы проверены!_",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    save_user(query.from_user.id)
    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data="back_main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📋 *ПРАВИЛА*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "1️⃣ _Подпишись на все каналы_\n"
        "2️⃣ _Нажми «Проверить подписку»_\n"
        "3️⃣ _Получи файл чита_\n\n"
        "⚠️ _Не кради файлы — поделись с друзьями!_\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "❗ *ДИСКЛЕЙМЕР*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "_Мы не являемся авторами кряков и не взламываем читы._\n"
        "_Мы берём кряки у проверенных сторонних источников._\n"
        "_Гарантии отсутствия вирусов мы не даём —_ *скачивай на свой страх и риск.*\n"
        "_Скачивая файлы, ты подтверждаешь, что понимаешь это._",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def back_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    save_user(query.from_user.id)

    keyboard = [
        [InlineKeyboardButton("⬇️  Скачать чит", callback_data="download")],
        [InlineKeyboardButton("💎  Наша база читов", callback_data="base")],
        [InlineKeyboardButton("📋  Правила", callback_data="rules")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ *ГЛАВНОЕ МЕНЮ*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Выбери действие 👇",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ У тебя нет доступа к этой команде.")
        return

    broadcast_state[ADMIN_ID] = True
    await update.message.reply_text(
        "📢 *РЕЖИМ РАССЫЛКИ*\n\n"
        "Отправь мне сообщение, которое хочешь разослать всем пользователям.\n"
        "Для отмены напиши /cancel",
        parse_mode="Markdown",
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id == ADMIN_ID:
        if broadcast_state.get(ADMIN_ID):
            broadcast_state[ADMIN_ID] = False
            await update.message.reply_text("❌ Рассылка отменена.")
            return
        if user_data.get(ADMIN_ID, {}).get("upload_state"):
            user_data.pop(ADMIN_ID, None)
            await update.message.reply_text("❌ Загрузка отменена.")
            return


async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID or not broadcast_state.get(ADMIN_ID):
        return

    broadcast_state[ADMIN_ID] = False
    users = load_users()
    sent = 0
    failed = 0

    for user_id in users:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=update.message.text,
                parse_mode="Markdown",
            )
            sent += 1
        except Exception:
            failed += 1

    await update.message.reply_text(
        f"✅ Рассылка завершена!\n"
        f"📨 Отправлено: {sent}\n"
        f"❌ Ошибок: {failed}",
    )


async def upload_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ У тебя нет доступа к этой команде.")
        return ConversationHandler.END

    user_data[ADMIN_ID] = {"upload_state": UPLOAD_NAME}
    await update.message.reply_text(
        "📤 *ЗАГРУЗКА ЧИТА*\n\n"
        "Напиши *название* чита (например: КРЯК MY CLIENT):",
        parse_mode="Markdown",
    )
    return UPLOAD_NAME


async def upload_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END

    cheat_name = update.message.text.strip()
    user_data[ADMIN_ID] = {"upload_state": UPLOAD_FILE, "upload_name": cheat_name}
    await update.message.reply_text(
        f"📤 *Название:* {cheat_name}\n\n"
        "Теперь отправь *файл* чита:",
        parse_mode="Markdown",
    )
    return UPLOAD_FILE


async def upload_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END

    document = update.message.document
    if not document:
        await update.message.reply_text("❌ Отправь именно *файл*, а не текст.", parse_mode="Markdown")
        return UPLOAD_FILE

    cheat_name = user_data.get(ADMIN_ID, {}).get("upload_name", "Unknown")
    safe_name =cheat_name.lower().replace(" ", "-").replace("кряк", "").replace("сурсы", "").strip("-")
    file_ext = Path(document.file_name).suffix if document.file_name else ".jar"
    filename = f"{safe_name}{file_ext}"
    file_path = f"cheats/{filename}"

    file = await document.get_file()
    CHEATS_DIR.mkdir(exist_ok=True)
    await file.download_to_drive(file_path)

    cheat_key = safe_name
    custom_cheats = load_custom_cheats()
    custom_cheats[cheat_key] = {
        "name": cheat_name,
        "files": [file_path],
    }
    save_custom_cheats(custom_cheats)

    user_data.pop(ADMIN_ID, None)

    await update.message.reply_text(
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "✅ *ЧИТ ЗАГРУЖЕН!*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📦 *Название:* {cheat_name}\n"
        f"📄 *Файл:* `{filename}`\n\n"
        "_Теперь он доступен в меню скачивания._",
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def upload_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.effective_user.id == ADMIN_ID:
        user_data.pop(ADMIN_ID, None)
        await update.message.reply_text("❌ Загрузка отменена.")
    return ConversationHandler.END


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    upload_handler = ConversationHandler(
        entry_points=[CommandHandler("upload", upload_start)],
        states={
            UPLOAD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, upload_name)],
            UPLOAD_FILE: [MessageHandler(filters.Document.ALL, upload_file)],
        },
        fallbacks=[CommandHandler("cancel", upload_cancel)],
    )

    app.add_error_handler(error_handler)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(upload_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, handle_broadcast))
    app.add_handler(CallbackQueryHandler(download, pattern="^download$"))
    app.add_handler(CallbackQueryHandler(base, pattern="^base$"))
    app.add_handler(CallbackQueryHandler(rules, pattern="^rules$"))
    app.add_handler(CallbackQueryHandler(back_main, pattern="^back_main$"))
    app.add_handler(CallbackQueryHandler(cheat_selected, pattern="^cheat_"))
    app.add_handler(CallbackQueryHandler(accept_rules, pattern="^accept_rules$"))
    app.add_handler(CallbackQueryHandler(check_subscription, pattern="^check_sub$"))

    logger.info("Bot started!")
    try:
        subprocess.run(["git", "pull"], capture_output=True, timeout=30)
    except Exception:
        pass
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
