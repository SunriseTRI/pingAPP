import time
import requests
from flask import Flask, jsonify
from telegram import Bot, Update
from telegram.ext import CommandHandler, Updater, CallbackContext
import os
import feedparser
import telegram
from dotenv import load_dotenv

app = Flask(__name__)

# Конфиг бота и сервера
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')  # Токен прописать в .env
RSS_URL = 'test_rss.xml'  # RSS-файл
USER_AGENT = 'Mozilla/5.0 (Linux; Android 10; Mobile)'  # User-Agent браузера Android
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Проверка на наличие токена
if TELEGRAM_TOKEN is None:
    raise ValueError("Токен бота не найден. Проверьте есть ли файл .env и заполнен ли.")

# Функция для обхода страниц из RSS
def ping_pages():
    print("Начинаю обход страниц...")
    feed = feedparser.parse(RSS_URL)
    results = []

    for entry in feed.entries:
        url = entry.link
        headers = {'User-Agent': USER_AGENT}
        try:
            start_time = time.time()
            response = requests.get(url, headers=headers)
            ping_time = (time.time() - start_time) * 1000
            results.append(f"{url} - Статус: {response.status_code} & Ping: {ping_time:.2f}ms")
        except Exception as e:
            results.append(f"Ошибка при обращении к {url}: {e}")

    print("Обход завершен.")
    return "\n".join(results)

# Сервер для ручного вызова обхода страниц
@app.route('/ping', methods=['GET'])
def ping():
    message = ping_pages()
    print(message)
    return jsonify({"message": message})

# Обработчик команды /start в боте
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Я бот для запуска обхода страниц.")

# Обработчик команды /ping для запуска обхода через бота
def ping_command(update: Update, context: CallbackContext):
    message = ping_pages()
    update.message.reply_text(message)

# Инициализация бота
def start_telegram_bot():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("ping", ping_command))

    updater.start_polling()
    updater.idle()

# Запуск бота и веб-сервера
if __name__ == '__main__':
    # Запуск бота в отдельном потоке
    import threading
    telegram_thread = threading.Thread(target=start_telegram_bot)
    telegram_thread.start()

    # Запуск веб-сервера Flask
    app.run(host='0.0.0.0', port=5000)
