import time
import requests
from flask import Flask, jsonify
from telegram import Bot, Update
from telegram.ext import CommandHandler, Updater, CallbackContext
import os
import feedparser

app = Flask(__name__)

# Получаем токен и RSS URL из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
RSS_URL = os.getenv("RSS_URL")
bot = Bot(token=TELEGRAM_TOKEN)

def ping_url(url):
    start_time = time.time()  # Запоминаем начальное время
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Linux; Android 10; Mobile)'})
    end_time = time.time()  # Запоминаем конечное время
    ping_time = end_time - start_time  # Вычисляем время пинга
    return response.status_code, ping_time  # Возвращаем статус и время пинга

@app.route('/ping', methods=['GET'])
def ping():
    feed = feedparser.parse(RSS_URL)
    results = {}

    for entry in feed.entries:
        url = entry.link
        status_code, ping_time = ping_url(url)  # Получаем статус и время пинга
        results[url] = {
            "status_code": status_code,
            "ping_time": ping_time
        }

    return jsonify({"message": "Обход завершен", "results": results})

# Telegram-бот
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Бот запущен. Используйте команду /ping для обхода страниц.")

def ping_command(update: Update, context: CallbackContext):
    update.message.reply_text("Начинаю обход страниц...")
    feed = feedparser.parse(RSS_URL)
    results = {}

    for entry in feed.entries:
        url = entry.link
        status_code, ping_time = ping_url(url)
        results[url] = {
            "status_code": status_code,
            "ping_time": ping_time
        }

    update.message.reply_text("Обход завершен. Результаты:\n" + "\n".join([f"{url}: {result['status_code']} (время пинга: {result['ping_time']:.2f} сек)" for url, result in results.items()]))

updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('ping', ping_command))

if __name__ == '__main__':
    updater.start_polling()
    app.run(debug=True)
