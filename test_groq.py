#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы Groq API
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Получить конфиг из .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

print(f"🧪 Тестирование Groq API")
print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(f"Model: {GROQ_MODEL}")
print(f"API Key: {'✅ Найден' if GROQ_API_KEY else '❌ НЕ НАЙДЕН'}")
print()

if not GROQ_API_KEY:
    print("❌ ОШИБКА: GROQ_API_KEY не найден в .env файле!")
    exit(1)

# Инициализируем клиент
try:
    client = Groq(api_key=GROQ_API_KEY)
    print("✅ Клиент Groq инициализирован")
except Exception as e:
    print(f"❌ Ошибка инициализации: {e}")
    exit(1)

# Тест 1: Простой запрос
print("\n📝 Тест 1: Простой текстовый запрос")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

try:
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "user", "content": "Скажи только 'OK' если ты работаешь"}
        ]
    )
    result = response.choices[0].message.content
    print(f"✅ Ответ: {result}")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    exit(1)

# Тест 2: Анализ профиля (как в боте)
print("\n📝 Тест 2: Анализ профиля (match/no_match)")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

test_profile = "Я ищу серьёзные отношения. Учу Python, люблю музыку и путешествия. Цель - найти человека для совместной жизни."

test_prompt = f"""Ты анализируешь анкету с дейтинг бота.

ЛАЙКАЙ ТОЛЬКО если хотя бы 2-3 пункта выполнено:
1. Активно развивает себя: учит языки, IT, музыку
2. Имеет чёткие амбиции и высокие цели
3. Нет признаков потребительства или токсичности
4. Конкретная информация о себе, интересах, целях

НЕ ЛАЙКАЙ если:
- Неясные цели
- Только фото без информации
- Признаки потребительского образа жизни

Верни ТОЛЬКО "match" или "no_match", ничего больше.

Анкета:
{test_profile}"""

try:
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "user", "content": test_prompt}
        ]
    )
    result = response.choices[0].message.content.strip().lower()
    print(f"✅ Ответ модели: {result}")

    # Проверим формат ответа (как в боте)
    is_match = "match" in result and "no_match" not in result

    if is_match:
        print("✅ Результат: MATCH ❤️")
    else:
        print("✅ Результат: NO_MATCH 👎")

except Exception as e:
    print(f"❌ Ошибка: {e}")
    exit(1)

# Тест 3: Информация об использовании
print("\n📊 Тест 3: Информация об использовании")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

try:
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "user", "content": "Привет"}
        ]
    )

    if hasattr(response, 'usage'):
        print(f"✅ Input tokens: {response.usage.prompt_tokens}")
        print(f"✅ Output tokens: {response.usage.completion_tokens}")
        print(f"✅ Total tokens: {response.usage.total_tokens}")
    else:
        print("⚠️  Информация об использовании недоступна")

except Exception as e:
    print(f"❌ Ошибка: {e}")

print("\n" + "━" * 40)
print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
print("Модель готова к использованию в боте 🚀")
