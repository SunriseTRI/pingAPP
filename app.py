import os
from dotenv import load_dotenv
import requests
from flask import Flask, request, jsonify
import feedparser
import telegram
from telegram.ext import CommandHandler, Updater

# Конфиг бота и сервера
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
RSS_URL = 'test_rss.xml'  # RSS-файл
USER_AGENT = 'Mozilla/5.0 (Linux; Android 10; Mobile)'  # User-Agent браузера Android

app = Flask(__name__)
bot = telegram.Bot(token=TELEGRAM_TOKEN)
# Проверка на наличие токена
if TELEGRAM_TOKEN is None:
    raise ValueError("Токен бота не найден. Проверьте есть ли файл .env и заполнен ли")
# Функция для обхода страниц из RSS
def ping_pages():
    feed = feedparser.parse(RSS_URL)
    for entry in feed.entries:
        url = entry.link
        headers = {'User-Agent': USER_AGENT}
        try:
            response = requests.get(url, headers=headers)
            print(f"Проверка страницы: {url} - Статус: {response.status_code}")
        except Exception as e:
            print(f"Ошибка при обращении к {url}: {e}")
    return "Обход завершен!"

# Сервер для ручного вызова обхода стр
@app.route('/ping', methods=['GET'])
def ping():
    message = ping_pages()
    return jsonify({"message": message})

# Обработчик команды /start в боте
def start(update, context):
    update.message.reply_text("Привет! Я бот для запуска обхода страниц.")

# Обработчик команды /ping для запуска обхода через
def ping_command(update, context):
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
