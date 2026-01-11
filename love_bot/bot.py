import asyncio
import json
import random
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, FSInputFile

from config import BOT_TOKEN, ALLOWED_USERS

# Пути к папкам
BASE_DIR = Path(__file__).parent
DATA = BASE_DIR / "data"
MOMENTS = BASE_DIR / "moments"
WB = BASE_DIR / "wb"
STICKERS_FILE = BASE_DIR / "stickers/stickers.txt"

# Загрузка текстов
def load_lines(filename):
    path = DATA / filename
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

compliments = load_lines("compliments.txt")
love_reasons = load_lines("love_reasons.txt")
memories = load_lines("memories.txt")
surprises = load_lines("surprises.txt")
no_order = load_lines("no_order.txt")
order_text = load_lines("order_text.txt")

# Музыка
music_list = []
music_file = BASE_DIR / "music.json"
if music_file.exists():
    with open(music_file, encoding="utf-8") as f:
        music_list = json.load(f)

# Стикеры — загружаем из файла
if STICKERS_FILE.exists():
    with open(STICKERS_FILE, encoding="utf-8") as f:
        STICKERS = [line.strip() for line in f if line.strip()]
else:
    STICKERS = []

# Список подбадривающих сообщений
CHEER_UP_MESSAGES = [
    "всё будет хорошо❤️",
    "Помни, что я всегда рядом 💌",
    "Всё в порядке всё пройдет",
    "Не грусти хорошая моя",
    "Я люблю тебя❤️",
    "Тебе нужно немножуо отдознуть",
    "Давай улыбнёмся вместе 😄",
    "Я горжусь тобой и твоими успехами 💖",
    "Каждый день с тобой особенный",
]

# Инициализация бота
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# Главное меню
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💬 Комплимент")],
        [KeyboardButton(text="❤️ Почему я тебя люблю")],
        [KeyboardButton(text="🕰 Воспоминание")],
        [KeyboardButton(text="📷 Момент")],
        [KeyboardButton(text="🎧 Музыка для тебя")],
        [KeyboardButton(text="🎁 Wildberries")],
        [KeyboardButton(text="✨ Сюрприз")],
        [KeyboardButton(text="😢 Мне грустно")]
    ],
    resize_keyboard=True
)

# Приватность — только для разрешенных пользователей
def private_only(func):
    async def wrapper(message: Message):
        if message.from_user.id not in ALLOWED_USERS:
            await message.answer("Этот бот не для вас.")
            return
        await func(message)
    return wrapper

# Старт
@dp.message(F.text == "/start")
@private_only
async def start(message: Message):
    await message.answer("Привет! Я здесь для тебя 🙂", reply_markup=menu)

# Отправка текста + случайного стикера
async def send_text_sticker(message: Message, texts):
    if texts:
        await message.answer(random.choice(texts))
        if STICKERS:
            await message.answer_sticker(random.choice(STICKERS))
    else:
        await message.answer("Пока нет содержимого.")

# Комплимент
@dp.message(F.text == "💬 Комплимент")
@private_only
async def compliment(message: Message):
    await send_text_sticker(message, compliments)

# Почему я люблю тебя
@dp.message(F.text == "❤️ Почему я тебя люблю")
@private_only
async def love(message: Message):
    await send_text_sticker(message, love_reasons)

# Воспоминание
@dp.message(F.text == "🕰 Воспоминание")
@private_only
async def memory(message: Message):
    await message.answer(random.choice(memories) if memories else "Воспоминания пока не добавлены.")

# Сюрприз — только из surprises.txt
@dp.message(F.text == "✨ Сюрприз")
@private_only
async def surprise(message: Message):
    if surprises:
        await message.answer(random.choice(surprises))
    else:
        await message.answer("Сюрпризы пока не добавлены.")

# Музыка
@dp.message(F.text == "🎧 Музыка для тебя")
@private_only
async def music(message: Message):
    if music_list:
        track = random.choice(music_list)
        text = (
            f"🎧 {track['title']} — {track['artist']}\n\n"
            f"{track['reason']}\n\n"
            f"{track['link']}"
        )
        await message.answer(text)
    else:
        await message.answer("Музыка пока не добавлена.")

# Моменты — поддержка .jpg, .jpeg, .png, .heif, .hfif
@dp.message(F.text == "📷 Момент")
@private_only
async def moment(message: Message):
    items = list(MOMENTS.glob("*.txt"))
    if items:
        chosen = random.choice(items)
        caption = chosen.read_text(encoding="utf-8")
        for ext in [".jpg", ".jpeg", ".png", ".heif", ".hfif"]:
            image = chosen.with_suffix(ext)
            if image.exists():
                await message.answer_photo(FSInputFile(image), caption=caption)
                return
        await message.answer(caption)
    else:
        await message.answer("Моменты пока не добавлены.")

# Wildberries — текст + QR + стикер
@dp.message(F.text == "🎁 Wildberries")
@private_only
async def wb(message: Message):
    qr = WB / "qr.png"
    if qr.exists() and order_text:
        text = random.choice(order_text)
        await message.answer_photo(FSInputFile(qr), caption=text)
        if STICKERS:
            await message.answer_sticker(random.choice(STICKERS))
    else:
        await message.answer(random.choice(no_order) if no_order else "Пока заказов нет.")

# Мне грустно — текст + стикер
@dp.message(F.text == "😢 Мне грустно")
@private_only
async def cheer_up(message: Message):
    await message.answer(random.choice(CHEER_UP_MESSAGES))
    if STICKERS:
        await message.answer_sticker(random.choice(STICKERS))

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
