import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from flask import Flask
from threading import Thread

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID", "-4891677163"))  # замени на свой ID группы

user_data = {}  # { user_id: {"name": "Tim", "utm": "instagram"} }

app = Flask('')

@app.route('/')
def home():
    return "Бот живой 💡"

@app.route('/status')
def status():
    if not user_data:
        return "Пока никто не писал 🤷‍♀️"
    response = "<h3>Пользователи, начавшие диалог:</h3><ul>"
    for uid, data in user_data.items():
        response += f"<li>{data['name']} — источник: <b>{data['utm']}</b></li>"
    response += "</ul>"
    return response

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    args = context.args
    utm_source = args[0] if args else "unknown"

    user_data[user.id] = {
        "name": f"@{user.username}" if user.username else user.first_name,
        "utm": utm_source
    }

    update.message.reply_text("👋 Добрый день! Пишите свой вопрос, мы на связи 💪")

    context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=f"🔔 @{user.username or user.first_name} начал диалог\nИсточник: {utm_source}"
    )

def forward(update: Update, context: CallbackContext):
    user = update.message.from_user
    if user.is_bot:
        return
    if update.effective_chat.id == GROUP_CHAT_ID:
        # Игнорируем сообщения из группы, чтобы не дублировать
        return

    context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=f"💬 Сообщение от @{user.username or user.first_name}:\n\n{update.message.text}"
    )

def main():
    Thread(target=run_flask).start()

    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, forward))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
