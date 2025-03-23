# model.py
import numpy as np
from keras.models import load_model
from PIL import Image, ImageOps

# Load the model
model = load_model("../BotAI(kodl)/keras_model.h5", compile=False)

# Load the labels
class_names = open("../BotAI(kodl)/labels.txt", "r", encoding="utf-8").readlines()

def predict_image(image_path):
    """Функция для предсказания класса изображения с использованием загруженной модели."""
    # Подготовка изображения для модели
    image = Image.open(image_path).convert("RGB")

    # Изменяем размер и нормализуем изображение
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

    # Создаем массив с правильной формой
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0] = normalized_image_array

    # Предсказание
    prediction = model.predict(data)
    index = np.argmax(prediction)
    class_name = class_names[index].strip()  # Убираем символы новой строки
    confidence_score = prediction[0][index]

    return class_name, confidence_score