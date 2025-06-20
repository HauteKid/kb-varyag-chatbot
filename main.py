import os
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID", "-4891677163"))

user_data = {}

app = Flask(__name__)
bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot, None, workers=0)  # для синхронной обработки

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

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dp.process_update(update)
    return "OK", 200

def start(update, context):
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

def forward(update, context):
    user = update.message.from_user
    if user.is_bot:
        return
    if update.effective_chat.id == GROUP_CHAT_ID:
        return

    context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=f"💬 Сообщение от @{user.username or user.first_name}:\n\n{update.message.text}"
    )

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, forward))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
