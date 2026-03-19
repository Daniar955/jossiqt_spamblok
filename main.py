import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import os
from flask import Flask
from threading import Thread

# Flask app для поддержания активности
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running! 🤖"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Запускаем веб-сервер
keep_alive()

# Настройки бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "5586220890"))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    
    if user_id == ADMIN_ID:
        await message.answer(
            "👋 Вы администратор.\n"
            "Все сообщения от пользователей будут приходить сюда.\n"
            "Чтобы ответить, просто напишите в ответ на сообщение."
        )
    else:
        await message.answer(
            "👋 Привет! Это анонимный бот.\n"
            "Напишите что-нибудь, и я передам это админу.\n"
            "Админ может вам ответить, и ответ придет сюда."
        )

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    
    if user_id == ADMIN_ID:
        if message.reply_to_message:
            try:
                original_text = message.reply_to_message.text or message.reply_to_message.caption
                if original_text and "ID: " in original_text:
                    user_id_line = [line for line in original_text.split('\n') if line.startswith("🆔 ID: ")][0]
                    target_user_id = int(user_id_line.replace("🆔 ID: ", ""))
                    
                    await bot.send_message(
                        target_user_id,
                        f"✉️ Ответ от админа:\n\n{message.text}"
                    )
                    await message.reply("✅ Ответ отправлен!")
                else:
                    await message.reply("❌ Не удалось определить, кому предназначен ответ.")
            except Exception as e:
                await message.reply(f"❌ Ошибка при отправке ответа: {e}")
        else:
            await message.reply("ℹ️ Чтобы ответить пользователю, используйте 'Ответить' на его сообщение.")
    
    else:
        try:
            await bot.send_message(
                ADMIN_ID,
                f"📨 Сообщение от пользователя:\n\n"
                f"{message.text or message.caption or '[Медиафайл]'}\n\n"
                f"🆔 ID: {user_id}\n"
                f"👤 Имя: {message.from_user.full_name}\n"
                f"🔗 Username: @{message.from_user.username if message.from_user.username else 'отсутствует'}"
            )
            
            if message.photo:
                await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, 
                                   caption=f"Фото от пользователя {user_id}")
            elif message.video:
                await bot.send_video(ADMIN_ID, message.video.file_id,
                                   caption=f"Видео от пользователя {user_id}")
            elif message.document:
                await bot.send_document(ADMIN_ID, message.document.file_id,
                                     caption=f"Документ от пользователя {user_id}")
            elif message.audio:
                await bot.send_audio(ADMIN_ID, message.audio.file_id,
                                   caption=f"Аудио от пользователя {user_id}")
            elif message.voice:
                await bot.send_voice(ADMIN_ID, message.voice.file_id)
            elif message.sticker:
                await bot.send_sticker(ADMIN_ID, message.sticker.file_id)
            
            await message.answer("✅ Сообщение доставлено админу!")
            
        except Exception as e:
            await message.answer("❌ Ошибка при отправке сообщения. Попробуйте позже.")
            logging.error(f"Ошибка отправки админу: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
