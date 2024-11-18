import logging
import asyncio
import aiohttp
import pdfplumber
from io import BytesIO
from telebot.async_telebot import AsyncTeleBot

# Замените на ваш токен
API_TOKEN = '7448506699:AAGK_bygLNREhA1N27CLkgpf6NHgw6KHN1Q'
bot = AsyncTeleBot(API_TOKEN)

PDF_URL = 'https://aitanapa.ru/download/%d1%80%d0%b0%d1%81%d0%bf%d0%b8%d1%81%d0%b0%d0%bd%d0%b8%d0%b5/?wpdmdl=970&refresh=673b6bdf508e11731947487'

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def fetch_pdf(session, url):
    """Асинхронно загружает PDF-файл."""
    try:
        async with session.get(url, timeout=10) as response:
            response.raise_for_status()
            return await response.read()
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка при загрузке PDF: {e}")
        return None


async def extract_text_from_pdf(pdf_bytes):
    """Извлекает текст из PDF-байтов."""
    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text(x_tolerance=2, y_tolerance=2)
                if page_text:
                    text += page_text + "\n"
            return text.strip()
    except pdfplumber.exceptions.EmptyFileError:
        logger.error("PDF-файл пуст")
        return "PDF-файл пуст."
    except Exception as e:
        logger.exception(f"Ошибка при извлечении текста из PDF: {e}")
        return f"Ошибка при извлечении текста из PDF: {e}"


async def get_schedule_from_pdf():
    """Асинхронно получает и обрабатывает расписание из PDF."""
    async with aiohttp.ClientSession() as session:
        pdf_bytes = await fetch_pdf(session, PDF_URL)
        if pdf_bytes:
            return await extract_text_from_pdf(pdf_bytes)
        else:
            return "Ошибка при загрузке PDF"


@bot.message_handler(commands=['schedule_pdf'])
async def send_schedule_pdf(message):
    """Обрабатывает команду /schedule_pdf, отправляет расписание."""
    schedule_text = await get_schedule_from_pdf()
    await bot.reply_to(message, schedule_text, parse_mode="HTML")


@bot.message_handler(commands=['start', 'help'])
async def send_welcome(message):
    """Обрабатывает команды /start и /help."""
    await bot.reply_to(message, "Привет! Используй команду /schedule_pdf, чтобы получить расписание.")


async def main():
    """Запускает бота."""
    try:
        await bot.infinity_polling()
    except Exception as e:
        logger.exception(f"Ошибка в основном цикле бота: {e}")


if __name__ == '__main__':
    asyncio.run(main())