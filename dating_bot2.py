import asyncio
import os
import requests
from dotenv import load_dotenv
from telethon import TelegramClient, events

# Загрузить переменные из .env файла
load_dotenv()

# === НАСТРОЙКИ ===
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_USERNAME = os.getenv("BOT_USERNAME", "@leomatchbot")

# LM Studio API
LM_STUDIO_API_URL = os.getenv("LM_STUDIO_API_URL", "http://localhost:1234/api/v1/chat")
LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL", "mistral-7b-instruct-v0.1")

# Параметры работы
MIN_PROFILE_LENGTH = int(os.getenv("MIN_PROFILE_LENGTH", "30"))
RESPONSE_DELAY = float(os.getenv("RESPONSE_DELAY", "1.5"))


TOO_MUCH_LIKES = '''
Слишком много ❤️ за сегодня.

Перейди на Premium и получи больше ❤️!
'''

MATCH_PROMPT = """
Ты анализируешь анкету с дейтинг бота. БУДЬ ОЧЕНЬ КРИТИЧЕН И ИЗБИРАТЕЛЕН.

ЛАЙКАЙ ТОЛЬКО если ЧТО-ТО из следующих условий выполнено:
1. Активно развивает себя: учит языки, развивается в IT/программировании, музыке или других серьёзных областях
2. Имеет чёткие амбиции и высокие цели (не просто живёт день за днём)
3. Ведёт здоровый образ жизни: нет признаков потребительства, аморального поведения или токсичности
4. Описание профиля содержит конкретную информацию о себе, интересах, целях (не пусто и не банально)
5. Девушка ищет отношения

ЛАЙКАЙ РЕДКО - большинство профилей должны получить "no_match".

НЕ ЛАЙКАЙ если:
- Неясные цели и амбиции
- Только фото без информации о себе
- Признаки потребительского или праздного образа жизни
- Банальное описание без деталей
- Хоть малейшие сомнения - ОТКЛОНИ

Верни ТОЛЬКО "match" или "no_match", ничего больше.
"""

RESPONSE_MATCH = "❤️"
RESPONSE_NO_MATCH = "👎"
RESPONSE_SKIP = "1 🚀"
# =================

client = TelegramClient("session", API_ID, API_HASH)


def analyze_profile(text: str) -> bool:
    prompt = f"{MATCH_PROMPT}\n\nАнкета:\n{text}"
    # Don't like empty profiles
    if not text or len(text.strip()) < MIN_PROFILE_LENGTH:
        return False
    try:
        response = requests.post(
            LM_STUDIO_API_URL,
            json={
                "model": LM_STUDIO_MODEL,
                "input": prompt
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        # output is a list, get first element's content
        output = data["output"][0]["content"].strip().lower()
        return "match" in output and "no_match" not in output
    except requests.exceptions.ConnectionError:
        print("[ERROR] Не удалось подключиться к LM Studio. Убедитесь, что:")
        print("  1. LM Studio запущен")
        print("  2. Сервер API активен на http://127.0.0.1:1234")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


@client.on(events.NewMessage(from_users=BOT_USERNAME))
async def handle_bot_message(event):
    text = event.message.text or ""
    if not text:
        return
    elif text.strip() == TOO_MUCH_LIKES.strip():
        print(f"[BOT] Получено:\n{text}\n")
        await client.disconnect()


    print(f"[BOT] Получено:\n{text}\n")

    try:
        is_match = await asyncio.to_thread(analyze_profile, text)
    except Exception as e:
        print(f"[ERROR] {e}")
        return

    reply = RESPONSE_MATCH if is_match else (RESPONSE_SKIP if text == "Нет такого варианта ответа" else RESPONSE_NO_MATCH)
    print(f"[{'СОВПАДЕНИЕ' if is_match else 'не совпало'}] → {reply!r}\n")

    await asyncio.sleep(RESPONSE_DELAY)
    await client.send_message(BOT_USERNAME, reply)


async def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║         ⚡ AutoLeoMatch by Phoenix ⚡                   ║
║                                                            ║
║      Automated Dating Profile Analyzer & Swiper           ║
║      Powered by Mistral-7B Neural Network                 ║
║                                                            ║
║  [>>>] Scanning... Analyzing... Matching...               ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """)
    await client.start()
    print(f"Слушаю {BOT_USERNAME}...")
    await client.run_until_disconnected()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[STOP] Выключение скрипта... До встречи! 👋\n")
        exit(0)