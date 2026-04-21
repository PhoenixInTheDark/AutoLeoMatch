import asyncio
import os
import requests
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.types import MessageEntityTextUrl
from openai import OpenAI                                                      

# Загрузить переменные из .env файла
load_dotenv()

# === НАСТРОЙКИ ===
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_USERNAME = os.getenv("BOT_USERNAME", "@leomatchbot")
YOUR_USERNAME = os.getenv("YOUR_USERNAME", "")
USE_OPENROUTER = os.getenv("USE_OPENROUTER", "true").lower() == "true"

if USE_OPENROUTER:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.io/api/v1",
        timeout=120.0  # 2 минуты таймаут для OpenRouter
    )
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct")
else:
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

ЛАЙКАЙ ТОЛЬКО если ХОТЯ БЫ 2-3 ПУНКТА из следующих условий выполнено:
1. Активно развивает себя: учит языки, развивается в IT/программировании, музыке или других серьёзных областях
2. Имеет чёткие амбиции и высокие цели (не просто живёт день за днём)
3. Нет признаков потребительства, аморального поведения или токсичности
4. Описание профиля содержит конкретную информацию о себе, интересах, целях (не пусто и не банально)


НЕ ЛАЙКАЙ если:
- Неясные цели и амбиции
- Только фото без информации о себе
- Признаки потребительского или праздного образа жизни
- Банальное описание без деталей
- девушка пишет на татарском
- анкеты с приглашениями в чатах

Моя анкета выглядит так:

Веб разработчик, 
IT блогер, 
специалист информационной безопасности, 
Студент программной инженерии. 
Несостоявшийся медбрат с дипломом вместо подставки под кофе и такой же несостоявшийся музыкант. 

Люблю музыку и книги в свободное время, смотреть сериалы в ориге, практиковать английский, монтировать видео, писать автоматизации для разных вещей (кстати, вероятнее всего этот лайк поставила нейронка на основе моих предпочтений личности) 

Планирую начать учить испанский.

Верни ТОЛЬКО "match" или "no_match", ничего больше.
"""

SMB_LIKED_YOU = "Отлично! Надеюсь хорошо проведете время 🙌"

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
        if USE_OPENROUTER:
            # Используем OpenRouter API
            response = openrouter_client.chat.completions.create(
                model=OPENROUTER_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            output = response.choices[0].message.content.strip().lower()
        else:
            # Используем LM Studio
            response = requests.post(
                LM_STUDIO_API_URL,
                json={
                    "model": LM_STUDIO_MODEL,
                    "input": prompt
                },
                timeout=300
            )
            response.raise_for_status()
            data = response.json()
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
        return
    elif SMB_LIKED_YOU.strip() in text.strip():
        print(f"[BOT] Получено:\n{text}\n")
        try:
            # Пытаемся получить предыдущее сообщение (анкету)
            msgs = await client.get_messages(event.message.peer_id, limit=10)
            if len(msgs) > 1:
                prev_msg = msgs[1]
                await client.forward_messages("me", prev_msg)
                print("[✅] Анкета переслана в Saved Messages")

            # Пересылаем уведомление о лайке
            await client.forward_messages("me", event.message)
            print("[✅] Уведомление о лайке переслано в Saved Messages\n")
        except Exception as e:
            print(f"[ERROR] Ошибка при пересылке: {e}\n")
        return


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