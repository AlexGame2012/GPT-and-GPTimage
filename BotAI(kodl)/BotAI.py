import os
import warnings
import logging
import telebot
from model import predict_image  # Импорт функции из model.py
from telebot import types
from io import BytesIO

# Игнорирование предупреждений
warnings.filterwarnings("ignore")

API_TOKEN = '7568512833:AAHLbVXNxyy2r17lovsN0y6SU9eneDjS4mY'
bot = telebot.TeleBot(API_TOKEN)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Словарь для кормления животных
feeding_guidelines = {
    "Рысь": "Кормите рысь мясом (кролики, птицы, мелкие млекопитающие).",
    "Волк": "Кормите волка мясом (олени, косули, зайцы, грызуны).",
    "Бегемот": "Кормите бегемота травами и водными растениями.",
    "Жираф": "Кормите жирафа листьями деревьев (особенно акаций).",
    "Лев": "Кормите льва мясом (антилопы, зебры, буйволы).",
    "Тигр": "Кормите тигра мясом (дикие копытные, свиньи, рыба).",
    "Белый медведь": "Кормите белого медведя рыбой (особенно тюленями) и морскими млекопитающими.",
    "Бурый медведь": "Кормите бурого медведя плодами, орехами, кореньями, рыбой и мясом.",
    "Лиса": "Кормите лису мясом (птицы, грызуны)."
}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет, добро пожаловать в бота!')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("/photo")
    item2 = types.KeyboardButton("/GPT")
    
    markup.add(item1, item2)
    bot.send_message(message.chat.id, 'Выберите команду:', reply_markup=markup)

@bot.message_handler(commands=['photo'])
def photo_command(message):
    bot.send_message(message.chat.id, "Отправьте фото животного из зоопарка (популярных) на обработку и мы скажем, чем его можно кормить.")

@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    try:
        logger.info("Получен запрос на загрузку фото.")
        if not message.photo:
            bot.send_message(message.chat.id, "Вы забыли загрузить картинку :(")
            return
        
        # Получаем информацию о файле
        file_info = bot.get_file(message.photo[-1].file_id)
        logger.info(f"ID файла: {file_info.file_id}")
        logger.info(f"Имя файла: {file_info.file_path}")

        # Загружаем файл в память
        downloaded_file = bot.download_file(file_info.file_path)
        image_stream = BytesIO(downloaded_file)

        # Используем импортированную функцию для предсказания
        class_name, confidence_score = predict_image(image_stream)
        confidence_score2 = confidence_score * 100

        if confidence_score2 >= 80:
            bot.send_message(message.chat.id, f"Животное: {class_name}\nДостоверность: {confidence_score2:.2f}%")
            feeding_message = feeding_guidelines.get(class_name, "Данное животное не найдено в памяти бота... :(")
            bot.send_message(message.chat.id, feeding_message)
        else:
            bot.send_message(message.chat.id, "Данное животное не найдено в памяти бота... :(")

    except Exception as e:
        logger.error(f"Произошла ошибка: {str(e)}")
        bot.send_message(message.chat.id, f"Произошла ошибка при обработке изображения. Пожалуйста, попробуйте снова.")


@bot.message_handler(commands=['kick09'])
def kick_user(message):
    if message.reply_to_message:
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id
        user_status = bot.get_chat_member(chat_id, user_id).status
        bot.kick_chat_member(chat_id, user_id)
        bot.reply_to(message, f"Пользователь {message.reply_to_message.from_user.username} был кикнут.")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите кикнуть.")

@bot.message_handler(commands=['GPT'])  # создание команды
def site(message):
    markup = types.InlineKeyboardMarkup()  # создаём кнопку
    web_info = types.WebAppInfo('https://gptchat.cloudpub.ru')  # ссылка для приложения
    button1 = types.InlineKeyboardButton("Открыть GPTchat", web_app=web_info)  # добавляем текст кнопки и указываем переменную
    markup.add(button1)  # добавляем кнопку
    bot.send_message(message.chat.id, "GPT A", reply_markup=markup)  # отправляем сообщение со встроенной кнопкой

if __name__ == "__main__":  # Исправлено на __name__
    print("Бот запущен и готов к работе.")
    bot.polling(none_stop=True)