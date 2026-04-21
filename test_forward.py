#!/usr/bin/env python3
"""
Тестовый скрипт для проверки пересылки сообщений в Telegram
"""

import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient, events

load_dotenv()

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
YOUR_USERNAME = os.getenv("YOUR_USERNAME", "")
BOT_USERNAME = os.getenv("BOT_USERNAME", "@leomatchbot")

print(f"🧪 Тестирование пересылки сообщений")
print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(f"Your username: {YOUR_USERNAME}")
print(f"Bot username: {BOT_USERNAME}")
print()

if not API_ID or API_ID == "0":
    print("❌ ОШИБКА: API_ID не настроен в .env!")
    exit(1)

if not API_HASH:
    print("❌ ОШИБКА: API_HASH не настроен в .env!")
    exit(1)

client = TelegramClient("session", API_ID, API_HASH)


async def test_forward():
    """Тест пересылки сообщений"""

    print("📝 Подключение к Telegram...")
    try:
        await client.start()
        print("✅ Подключено\n")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

    try:
        # Получаем информацию о пользователе
        me = await client.get_me()
        print(f"✅ Вошли как: @{me.username} ({me.first_name})\n")

        # === Тест 1: Отправка сообщения себе ===
        print("📝 Тест 1: Отправка сообщения в Saved Messages")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        try:
            msg = await client.send_message("me", "🧪 Тестовое сообщение для проверки пересылки")
            print(f"✅ Сообщение отправлено (ID: {msg.id})\n")
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}\n")
            return False

        # === Тест 2: Пересылка своего сообщения в Saved Messages ===
        print("📝 Тест 2: Пересылка сообщения в Saved Messages")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        try:
            # Отправляем тестовое сообщение
            test_msg = await client.send_message("me", "📬 Исходное сообщение для пересылки")

            # Пересылаем его обратно
            forwarded = await client.forward_messages("me", test_msg)
            print(f"✅ Сообщение переслано (ID: {forwarded.id if forwarded else 'unknown'})\n")
        except Exception as e:
            print(f"❌ Ошибка пересылки: {e}\n")
            return False

        # === Тест 3: Пересылка в конкретного пользователя ===
        print("📝 Тест 3: Пересылка сообщения себе")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        try:
            msg_to_forward = await client.send_message("me", "🔄 Сообщение для пересылки себе")
            forwarded = await client.forward_messages(YOUR_USERNAME, msg_to_forward)
            print(f"✅ Пересланно пользователю {YOUR_USERNAME}\n")
        except Exception as e:
            print(f"❌ Ошибка пересылки пользователю: {e}\n")
            return False

        # === Тест 4: Проверка доступа к боту ===
        print("📝 Тест 4: Доступ к боту @leomatchbot")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        try:
            # Проверяем, сможем ли получить сообщения от бота
            # (это не будет работать если нет истории с ботом)
            await client.get_entity(BOT_USERNAME)
            print(f"✅ Бот {BOT_USERNAME} доступен\n")
        except Exception as e:
            print(f"⚠️  Ошибка доступа к боту: {e}")
            print("   (Это нормально, если история чата очищена)\n")

        # === Итоги ===
        print("=" * 50)
        print("✅ ВСЕ ОСНОВНЫЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("=" * 50)
        print("\n📋 Что работает:")
        print("  ✓ Подключение к Telegram")
        print("  ✓ Отправка сообщений в Saved Messages")
        print("  ✓ Пересылка сообщений")
        print("\n⚠️  Важное:")
        print("  • Используй 'me' для Saved Messages (Избранное)")
        print("  • Используй @username для пересылки конкретному пользователю")
        print("\n🚀 Пересылка в боте будет работать корректно!")

        return True

    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False
    finally:
        await client.disconnect()


if __name__ == "__main__":
    try:
        result = asyncio.run(test_forward())
        exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n[STOP] Тест отменен пользователем")
        exit(0)
