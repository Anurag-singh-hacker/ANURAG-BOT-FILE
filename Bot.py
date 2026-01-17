import telebot, json, os

BOT_TOKEN = "8310671853:AAHwbyjsU922Ft-1mJgOmyOfIyddKe99yBc"
ADMIN_ID = 6826304542     # <-- आपका Telegram ID

bot = telebot.TeleBot(BOT_TOKEN)
DATA_FILE = "data.json"

# ---------- LOAD DATA ----------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"folders": {}, "recent": []}

def save_data(db):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

db = load_data()

# ========== USER SIDE ==========

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.InlineKeyboardMarkup()

    for folder in db["folders"]:
        markup.add(
            telebot.types.InlineKeyboardButton(
                folder, callback_data=f"folder|{folder}"
            )
        )

    bot.send_message(
        message.chat.id,
        "📁 Select a folder:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("folder|"))
def open_folder(call):
    folder = call.data.split("|")[1]

    if folder not in db["folders"] or not db["folders"][folder]:
        bot.answer_callback_query(call.id, "Empty folder!")
        return

    markup = telebot.types.InlineKeyboardMarkup()

    for name, info in db["folders"][folder].items():
        link = info["link"]

        markup.add(
            telebot.types.InlineKeyboardButton(
                name,
                url=link   # 👉 CLICK KARTE HI WEBSITE OPEN
            )
        )

    bot.send_message(
        call.message.chat.id,
        f"📁 {folder} files:",
        reply_markup=markup
    )

# ========== ADMIN SIDE (website ke liye same logic) ==========

@bot.message_handler(commands=['addfolder'])
def add_folder(message):
    if message.from_user.id != ADMIN_ID:
        return

    folder = message.text.split(" ",1)[1].strip()
    db["folders"].setdefault(folder, {})
    save_data(db)
    bot.send_message(message.chat.id, f"📁 Folder created: {folder}")

@bot.message_handler(commands=['addlink'])
def add_link(message):
    if message.from_user.id != ADMIN_ID:
        return

    data = message.text.split(" ",1)[1]
    folder, name, link, *rest = [x.strip() for x in data.split("|")]
    thumb = rest[0] if rest else ""

    db["folders"].setdefault(folder, {})
    db["folders"][folder][name] = {"link": link, "thumb": thumb}
    db["recent"].insert(0, f"{folder} → {name}")
    db["recent"] = db["recent"][:10]

    save_data(db)
    bot.send_message(message.chat.id, f"✅ Saved: {folder} / {name}")

@bot.message_handler(commands=['editlink'])
def edit_link(message):
    if message.from_user.id != ADMIN_ID:
        return

    data = message.text.split(" ",1)[1]
    folder, name, newlink = [x.strip() for x in data.split("|")]

    if folder in db["folders"] and name in db["folders"][folder]:
        db["folders"][folder][name]["link"] = newlink
        save_data(db)
        bot.send_message(message.chat.id, "✏️ Updated link!")

@bot.message_handler(commands=['dellink'])
def delete_link(message):
    if message.from_user.id != ADMIN_ID:
        return

    data = message.text.split(" ",1)[1]
    folder, name = [x.strip() for x in data.split("|")]

    if folder in db["folders"] and name in db["folders"][folder]:
        del db["folders"][folder][name]
        save_data(db)
        bot.send_message(message.chat.id, "🗑 Deleted!")

@bot.message_handler(commands=['delfolder'])
def delete_folder(message):
    if message.from_user.id != ADMIN_ID:
        return

    folder = message.text.split(" ",1)[1].strip()
    if folder in db["folders"]:
        del db["folders"][folder]
        save_data(db)
        bot.send_message(message.chat.id, "🗑 Folder deleted!")

print("Bot running...")
bot.infinity_polling()
