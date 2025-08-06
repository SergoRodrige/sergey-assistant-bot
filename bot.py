import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import openai

# Загружаем переменные окружения из .env (если локальный запуск)
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

openai.api_key = OPENAI_API_KEY

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Финальный промпт — здесь можно менять стиль общения
FINAL_PROMPT = """
Ты мой универсальный помощник.
Ты умеешь помогать в фриланс-задачах: поиск клиентов, управление проектами, напоминания, рассылки, выставление счетов, аналитика.
Также ты умеешь помогать в бытовых делах: покупки, планирование, контроль бюджета, рекомендации.
Отвечай дружелюбно, но чётко. Будь практичным и по делу.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой универсальный помощник. Напиши, чем помочь.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": FINAL_PROMPT},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        answer = response["choices"][0]["message"]["content"]
        await update.message.reply_text(answer)

    except Exception as e:
        logging.error(f"Ошибка OpenAI: {e}")
        await update.message.reply_text("Произошла ошибка при обращении к ИИ. Проверь API ключ.")

def main():
    if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
        logging.error("Отсутствует TELEGRAM_TOKEN или OPENAI_API_KEY")
        return

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("Бот запущен...")
    app.run_polling()

if name == "__main__":
    main()
