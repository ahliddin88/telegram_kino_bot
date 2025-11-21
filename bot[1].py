# Telegram Kino Bot - Enhanced (PTB v20+/v21+ compatible)
# Prepared for Abu oka. Add TOKEN, ADMIN_ID and CHANNEL_ID at top.

import logging
import json, os, uuid
from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto,
    InlineQueryResultArticle, InputTextMessageContent
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    filters, ContextTypes, InlineQueryHandler
)

# ====== LOGGING ======
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ====== CONFIG ======
TOKEN = "8251274371:AAEPiiJaDo8IGB-_LaU7zkiRBap2EiO1GQU"
ADMIN_ID = 8092708766
CHANNEL_ID = "@kinolaruzhdtarjima"

# ====== DB ======
DB_FILE = "movies.json"
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)

def load_movies():
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_movies(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ====== HELP / START ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom Abu oka! 🎬\nKino bot tayyor.\nCommands:\n/addmovie name|link|optional_image_url\n/list\n/get <index>\n/del <index>\n/postall"
    )

# ====== ADD MOVIE (supports pipe-separated fields) ======
async def add_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.id
    if user != ADMIN_ID:
        return await update.message.reply_text("⛔ Siz admin emassiz!")

    text = update.message.text.partition(" ")[2].strip()
    if not text:
        return await update.message.reply_text("Foydalanish: /addmovie name|link|image_url(optional)")

    parts = [p.strip() for p in text.split("|")]
    name = parts[0]
    link = parts[1] if len(parts) > 1 else ""
    image = parts[2] if len(parts) > 2 else ""

    movies = load_movies()
    movies.append({"name": name, "link": link, "image": image})
    save_movies(movies)

    await update.message.reply_text("🎬 Kino qo'shildi!")

# ====== LIST MOVIES ======
async def list_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movies = load_movies()
    if not movies:
        return await update.message.reply_text("❌ Kino mavjud emas!")

    lines = []
    for i, m in enumerate(movies, 1):
        lines.append(f"{i}. {m.get('name','-')} — {m.get('link','-')}")
    await update.message.reply_text("📚 Kinolar ro'yxati:\n" + "\n".join(lines))

# ====== GET MOVIE (by index) ======
async def get_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movies = load_movies()
    args = context.args
    if not args:
        return await update.message.reply_text("Foydalanish: /get <index>")

    try:
        idx = int(args[0]) - 1
        m = movies[idx]
    except Exception:
        return await update.message.reply_text("Noto'g'ri indeks.")

    text = f"🎬 *{m.get('name','')}*\n{m.get('link','')}"
    if m.get("image"):
        await update.message.reply_photo(photo=m["image"], caption=text, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, parse_mode="Markdown")

# ====== DELETE MOVIE ======
async def del_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.id
    if user != ADMIN_ID:
        return await update.message.reply_text("⛔ Siz admin emassiz!")

    args = context.args
    if not args:
        return await update.message.reply_text("Foydalanish: /del <index>")

    try:
        idx = int(args[0]) - 1
        movies = load_movies()
        removed = movies.pop(idx)
        save_movies(movies)
        await update.message.reply_text(f"🗑️ O'chirildi: {removed.get('name')}")
    except Exception:
        return await update.message.reply_text("Noto'g'ri indeks yoki xatolik.")

# ====== POST ALL TO CHANNEL ======
async def post_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.id
    if user != ADMIN_ID:
        return await update.message.reply_text("⛔ Ruxsat yo'q!")

    movies = load_movies()
    if not movies:
        return await update.message.reply_text("❌ Hech qanday kino yo'q!")

    for m in movies:
        text = f"🎬 *{m.get('name','')}*\n{m.get('link','')}"
        if m.get("image"):
            try:
                await context.bot.send_photo(chat_id=CHANNEL_ID, photo=m["image"], caption=text, parse_mode="Markdown")
            except Exception as e:
                await context.bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="Markdown")
        else:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="Markdown")

    await update.message.reply_text("📤 Hammasi kanalga yuborildi!")

# ====== INLINE SEARCH (simple) ======
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query.lower()
    results = []
    movies = load_movies()

    if not query:
        # show first 10 if empty
        sample = movies[:10]
    else:
        sample = [m for m in movies if query in m.get("name","").lower()][:20]

    for i, m in enumerate(sample):
        idd = str(uuid.uuid4())
        title = m.get("name","")
        content = InputTextMessageContent(f"🎬 *{title}*\n{m.get('link','')}", parse_mode="Markdown")
        results.append(InlineQueryResultArticle(id=idd, title=title, input_message_content=content))

    await update.inline_query.answer(results[:50])

# ====== ADMIN PANEL (callback) ======
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return await update.message.reply_text("⛔ Ruxsat yo'q!")

    keyboard = [
        [InlineKeyboardButton("🎬 Kino qo'shish", callback_data="add_movie")],
        [InlineKeyboardButton("📚 Kinolar ro'yxati", callback_data="list_movies")],
        [InlineKeyboardButton("📤 Kanalga yuborish", callback_data="post_all")],
    ]
    await update.message.reply_text("Admin panelga xush kelibsiz!", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "list_movies":
        return await list_movies(q, context)
    if q.data == "post_all":
        return await post_all(q, context)

# ====== MAIN ======
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addmovie", add_movie))
    application.add_handler(CommandHandler("list", list_movies))
    application.add_handler(CommandHandler("get", get_movie))
    application.add_handler(CommandHandler("del", del_movie))
    application.add_handler(CommandHandler("postall", post_all))
    application.add_handler(CommandHandler("admin", admin_panel))

    application.add_handler(CallbackQueryHandler(admin_buttons))
    application.add_handler(InlineQueryHandler(inline_query))

    logger.info("Bot ishga tushdi...")
    application.run_polling()

if __name__ == "__main__":
    main()