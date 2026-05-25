# AutoLeoMatch by Phoenix

<p align="center">
  <img src="logo.jpg" alt="AutoLeoMatch logo" width="240">
</p>

Автоматизированный Python-скрипт для анализа и свайпинга анкет в Telegram-боте **@leomatchbot** с использованием AI.

Проект работает через Telegram user session: скрипт подключается к вашему Telegram-аккаунту через Telethon, читает сообщения от LeoMatch и отправляет ответы от имени аккаунта.

## Версии и ветки

- `main` - обычная локальная версия для ручного запуска. Если LeoMatch сообщает о дневном лимите лайков или отсутствии анкет, скрипт завершает работу.
- `version_for_server` - серверная версия для долгого фонового запуска на VPS, `tmux`, `screen`, `systemd` или другом process manager. При лимите лайков или отсутствии анкет скрипт ждет 1 час, снова запускает диалог и продолжает работу.

English branch overview:

- `main` is the standard local edition for manual runs. It is best for one-off sessions on a personal machine. When LeoMatch reports the daily like limit or no available profiles, the script exits instead of waiting in the background. This branch also supports Docker Compose for local containerized runs.
- `version_for_server` is the server edition for continuous background usage on a VPS, `tmux`, `screen`, `systemd`, Docker Compose, or another process manager. When LeoMatch reports the daily like limit or no available profiles, the script waits for 1 hour, starts the dialog again, and keeps working without manual intervention.

Для локального использования обычно достаточно ветки `main`. Для постоянной работы на сервере используйте:

```bash
git checkout version_for_server
```

## Что умеет

- Анализирует текст анкеты через OpenAI-compatible Chat Completions API или локальный LM Studio.
- Ставит лайк, если анкета соответствует заданным критериям.
- Пропускает неподходящие и слишком короткие анкеты.
- Пересылает найденные мэтчи и уведомления о лайках в Saved Messages.
- Обрабатывает системные сообщения LeoMatch и продолжает работу без зависания.
- В `main` останавливается при лимите лайков или когда бот сообщает, что анкет больше нет.
- В `version_for_server` ждет и пытается продолжить работу позже.

## Требования

- Python 3.8+
- Telegram account и API credentials с https://my.telegram.org/apps
- Интернет-соединение
- Docker и Docker Compose, если нужен запуск в контейнере
- Один из AI-провайдеров:
  - OpenRouter или другой OpenAI-compatible endpoint
  - LM Studio с локально запущенным API

## Установка

```bash
git clone https://github.com/PhoenixInTheDark/AutoLeoMatch.git
cd AutoLeoMatch
```

Если нужна серверная версия, переключитесь на ветку сразу после клонирования:

```bash
git checkout version_for_server
```

Затем установите зависимости:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

На Windows активация окружения:

```bash
venv\Scripts\activate
```

## Настройка

Заполните `.env` своими значениями:

```env
# Telegram API Credentials
API_ID=your_api_id_here
API_HASH=your_api_hash_here

# Бот для автолайков
BOT_USERNAME=@leomatchbot
YOUR_USERNAME=your_telegram_username_here

# true - OpenRouter/OpenAI-compatible API, false - LM Studio
USE_OPENROUTER=true

# OpenRouter/OpenAI-compatible API
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=google/gemma-4-31b-it:free

# Опционально: endpoint совместимого сервиса.
# Если не указан, код использует https://openrouter.io/api/v1
BASE_URL=https://routerai.ru/api/v1

# LM Studio API, если USE_OPENROUTER=false
# LM_STUDIO_API_URL=http://localhost:1234/api/v1/chat
# LM_STUDIO_MODEL=mistral-7b-instruct-v0.1

# Параметры работы
MIN_PROFILE_LENGTH=30
RESPONSE_DELAY=1.5
```

`BASE_URL` нужен только если вы используете не стандартный OpenRouter endpoint или совместимый сервис. Для обычного OpenRouter можно удалить эту переменную из `.env`.

## Запуск

```bash
python dating_bot2.py
```

При первом запуске Telethon может запросить авторизацию Telegram. После подключения скрипт слушает сообщения от `BOT_USERNAME` и отвечает лайком или дизлайком.

После успешной авторизации рядом со скриптом появится файл `session.session`. Он нужен для повторных запусков без ввода кода Telegram.

Остановка:

```text
Ctrl+C
```

## Запуск через Docker Compose

В ветке `main` для запуска через Docker Compose используйте одноразовую команду:

```bash
docker-compose run --rm bot
```

При первом запуске Telethon попросит войти в Telegram: ввести номер телефона, код подтверждения и, если включена двухфакторная защита, пароль. После успешной авторизации рядом со скриптом появится файл `session.session`.

Текущий `docker-compose.yml` монтирует каталог проекта в контейнер как `/app`, поэтому `session.session` хранится на хосте рядом с кодом и переживает пересборку контейнера. `.env` передается в контейнер через `env_file`, а `.dockerignore` не дает секретам и файлам сессии попасть в образ при сборке.

Если у вас установлен новый Docker Compose Plugin, вместо `docker-compose` можно использовать `docker compose`:

```bash
docker compose run --rm bot
```

## Серверный запуск

Для постоянной работы используйте ветку `version_for_server`.

Перед запуском в фоне выполните скрипт один раз в интерактивной SSH-сессии, чтобы пройти авторизацию Telegram и создать `session.session`:

```bash
source venv/bin/activate
python dating_bot2.py
```

После этого можно запускать скрипт в `tmux`:

```bash
tmux new -s autoleomatch
cd /path/to/AutoLeoMatch
source venv/bin/activate
python dating_bot2.py
```

Или через `systemd`:

```ini
[Unit]
Description=AutoLeoMatch
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/path/to/AutoLeoMatch
ExecStart=/path/to/AutoLeoMatch/venv/bin/python /path/to/AutoLeoMatch/dating_bot2.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

В `systemd` важно указать `WorkingDirectory` на каталог проекта, где лежит `session.session`.

## Критерии отбора

Текущий prompt лайкает только анкеты, где человек:

- ищет отношения;
- хочет длительного общения;
- увлекается содержательными темами вроде IT, музыки или рисования;
- не пишет бессмысленный или явно неподходящий текст.

Анкеты короче `MIN_PROFILE_LENGTH` символов автоматически отклоняются без запроса к модели.

## Проверка

Быстрая локальная проверка синтаксиса:

```bash
python -m py_compile dating_bot2.py test_openrouter.py test_groq.py test_forward.py
```

Проверка OpenRouter/OpenAI-compatible API:

```bash
python test_openrouter.py
```

Проверка Telegram-пересылки:

```bash
python test_forward.py
```

`test_groq.py` оставлен как отдельная ручная проверка Groq API. Основной бот сейчас напрямую Groq не использует.

## Структура проекта

```text
AutoLeoMatch/
├── dating_bot2.py       # Основной скрипт
├── Dockerfile           # Образ для запуска бота в контейнере
├── docker-compose.yml   # Запуск через Docker Compose
├── .dockerignore        # Исключения для Docker build context
├── .env.example         # Пример конфигурации
├── requirements.txt     # Python зависимости
├── test_openrouter.py   # Ручная проверка OpenRouter/OpenAI-compatible API
├── test_forward.py      # Ручная проверка Telegram-пересылки
├── test_groq.py         # Ручная проверка Groq API
└── README.md
```

## Зависимости

Основные библиотеки:

- `telethon` для Telegram API
- `openai` для OpenRouter и совместимых Chat Completions API
- `requests` для LM Studio
- `python-dotenv` для загрузки `.env`

## Решение проблем

### Не подключается к Telegram

Проверьте `API_ID`, `API_HASH`, интернет-соединение и наличие доступа к Telegram. При необходимости удалите старый `session.session` и авторизуйтесь заново.

### systemd запускает сервис, но Telegram снова просит код

Проверьте, что `WorkingDirectory` указывает на каталог проекта, где лежит `session.session`. Telethon ищет файл сессии относительно рабочей директории.

### Docker Compose запускает контейнер, но Telegram снова просит код

Проверьте, что в `docker-compose.yml` каталог проекта смонтирован в `/app`:

```yaml
volumes:
  - .:/app
```

Файл `session.session` должен лежать рядом с `dating_bot2.py` на хосте. Если его нет, создайте сессию через `docker-compose run --rm bot` и пройдите интерактивную авторизацию Telegram.

### Не работает OpenRouter или совместимый endpoint

Проверьте `OPENROUTER_API_KEY`, `OPENROUTER_MODEL` и `BASE_URL`. Для стандартного OpenRouter удалите `BASE_URL` или установите:

```env
BASE_URL=https://openrouter.io/api/v1
```

### Не подключается LM Studio

Если `USE_OPENROUTER=false`, убедитесь, что LM Studio запущен, API Server включен, модель загружена, а `LM_STUDIO_API_URL` указывает на правильный адрес.

### Скрипт лайкает не тех людей

Критерии находятся в `MATCH_PROMPT` внутри `dating_bot2.py`. Измените prompt и проверьте поведение на нескольких тестовых анкетах перед длительным запуском.

## Безопасность

- Не коммитьте `.env` с реальными ключами и Telegram credentials.
- Не коммитьте `session.session`: он дает доступ к авторизованной Telegram-сессии.
- Используйте только свой Telegram account и свои API credentials.
- Учитывайте правила Telegram и LeoMatch при автоматизации действий.

## English

Automated Python script for analyzing and swiping profiles in the Telegram bot **@leomatchbot** using AI.

The project works through a Telegram user session: the script connects to your Telegram account via Telethon, reads messages from LeoMatch, and sends replies on behalf of the account.

## Versions and branches

- `main` - the regular local version for manual runs. If LeoMatch reports the daily like limit or no available profiles, the script exits.
- `version_for_server` - the server version for long-running background usage on a VPS, `tmux`, `screen`, `systemd`, or another process manager. When the like limit is reached or no profiles are available, the script waits 1 hour, starts the dialog again, and continues working.

For local usage, the `main` branch is usually enough. For continuous server usage, use:

```bash
git checkout version_for_server
```

## Features

- Analyzes profile text through an OpenAI-compatible Chat Completions API or local LM Studio.
- Likes profiles that match the configured criteria.
- Skips unsuitable and too-short profiles.
- Forwards found matches and like notifications to Saved Messages.
- Handles LeoMatch system messages and keeps working without hanging.
- In `main`, stops when the like limit is reached or when the bot reports that there are no more profiles.
- In `version_for_server`, waits and tries to continue later.

## Requirements

- Python 3.8+
- Telegram account and API credentials from https://my.telegram.org/apps
- Internet connection
- Docker and Docker Compose if you want to run the bot in a container
- One of the AI providers:
  - OpenRouter or another OpenAI-compatible endpoint
  - LM Studio with a locally running API

## Installation

```bash
git clone https://github.com/PhoenixInTheDark/AutoLeoMatch.git
cd AutoLeoMatch
```

If you need the server version, switch branches right after cloning:

```bash
git checkout version_for_server
```

Then install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

On Windows, activate the environment with:

```bash
venv\Scripts\activate
```

## Configuration

Fill `.env` with your own values:

```env
# Telegram API Credentials
API_ID=your_api_id_here
API_HASH=your_api_hash_here

# Bot for auto-likes
BOT_USERNAME=@leomatchbot
YOUR_USERNAME=your_telegram_username_here

# true - OpenRouter/OpenAI-compatible API, false - LM Studio
USE_OPENROUTER=true

# OpenRouter/OpenAI-compatible API
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=google/gemma-4-31b-it:free

# Optional: compatible service endpoint.
# If not specified, the code uses https://openrouter.io/api/v1
BASE_URL=https://routerai.ru/api/v1

# LM Studio API, if USE_OPENROUTER=false
# LM_STUDIO_API_URL=http://localhost:1234/api/v1/chat
# LM_STUDIO_MODEL=mistral-7b-instruct-v0.1

# Runtime settings
MIN_PROFILE_LENGTH=30
RESPONSE_DELAY=1.5
```

`BASE_URL` is needed only if you use a non-standard OpenRouter endpoint or a compatible service. For regular OpenRouter, you can remove this variable from `.env`.

## Running

```bash
python dating_bot2.py
```

On the first run, Telethon may ask you to authorize Telegram. After connecting, the script listens for messages from `BOT_USERNAME` and replies with a like or dislike.

After successful authorization, a `session.session` file will appear next to the script. It is needed for repeated runs without entering the Telegram code again.

Stop the script with:

```text
Ctrl+C
```

## Running with Docker Compose

In the `main` branch, use this one-time command to run with Docker Compose:

```bash
docker-compose run --rm bot
```

On the first run, Telethon will ask you to log in to Telegram: enter your phone number, confirmation code, and, if two-factor authentication is enabled, your password. After successful authorization, a `session.session` file will appear next to the script.

The current `docker-compose.yml` mounts the project directory into the container as `/app`, so `session.session` is stored on the host next to the code and survives container rebuilds. `.env` is passed into the container through `env_file`, and `.dockerignore` prevents secrets and session files from getting into the image during build.

If you have the newer Docker Compose Plugin installed, you can use `docker compose` instead of `docker-compose`:

```bash
docker compose run --rm bot
```

## Server run

For continuous usage, use the `version_for_server` branch.

Before starting the script in the background, run it once in an interactive SSH session to authorize Telegram and create `session.session`:

```bash
source venv/bin/activate
python dating_bot2.py
```

After that, you can run the script in `tmux`:

```bash
tmux new -s autoleomatch
cd /path/to/AutoLeoMatch
source venv/bin/activate
python dating_bot2.py
```

Or through `systemd`:

```ini
[Unit]
Description=AutoLeoMatch
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/path/to/AutoLeoMatch
ExecStart=/path/to/AutoLeoMatch/venv/bin/python /path/to/AutoLeoMatch/dating_bot2.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

With `systemd`, it is important to set `WorkingDirectory` to the project directory where `session.session` is located.

## Selection criteria

The current prompt likes only profiles where the person:

- is looking for a relationship;
- wants long-term communication;
- is interested in meaningful topics such as IT, music, or drawing;
- does not write meaningless or clearly unsuitable text.

Profiles shorter than `MIN_PROFILE_LENGTH` characters are automatically rejected without sending a request to the model.

## Checks

Quick local syntax check:

```bash
python -m py_compile dating_bot2.py test_openrouter.py test_groq.py test_forward.py
```

OpenRouter/OpenAI-compatible API check:

```bash
python test_openrouter.py
```

Telegram forwarding check:

```bash
python test_forward.py
```

`test_groq.py` is kept as a separate manual check for the Groq API. The main bot does not currently use Groq directly.

## Project structure

```text
AutoLeoMatch/
├── dating_bot2.py       # Main script
├── Dockerfile           # Image for running the bot in a container
├── docker-compose.yml   # Run with Docker Compose
├── .dockerignore        # Docker build context exclusions
├── .env.example         # Example configuration
├── requirements.txt     # Python dependencies
├── test_openrouter.py   # Manual OpenRouter/OpenAI-compatible API check
├── test_forward.py      # Manual Telegram forwarding check
├── test_groq.py         # Manual Groq API check
└── README.md
```

## Dependencies

Main libraries:

- `telethon` for Telegram API
- `openai` for OpenRouter and compatible Chat Completions APIs
- `requests` for LM Studio
- `python-dotenv` for loading `.env`

## Troubleshooting

### Cannot connect to Telegram

Check `API_ID`, `API_HASH`, your internet connection, and Telegram access. If needed, delete the old `session.session` and authorize again.

### systemd starts the service, but Telegram asks for the code again

Check that `WorkingDirectory` points to the project directory where `session.session` is located. Telethon looks for the session file relative to the working directory.

### Docker Compose starts the container, but Telegram asks for the code again

Check that the project directory is mounted to `/app` in `docker-compose.yml`:

```yaml
volumes:
  - .:/app
```

The `session.session` file must be next to `dating_bot2.py` on the host. If it is missing, create the session with `docker-compose run --rm bot` and complete the interactive Telegram authorization.

### OpenRouter or a compatible endpoint does not work

Check `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, and `BASE_URL`. For standard OpenRouter, remove `BASE_URL` or set it to:

```env
BASE_URL=https://openrouter.io/api/v1
```

### Cannot connect to LM Studio

If `USE_OPENROUTER=false`, make sure LM Studio is running, API Server is enabled, the model is loaded, and `LM_STUDIO_API_URL` points to the correct address.

### The script likes the wrong people

The criteria are located in `MATCH_PROMPT` inside `dating_bot2.py`. Change the prompt and test the behavior on several sample profiles before a long run.

## Security

- Do not commit `.env` with real keys and Telegram credentials.
- Do not commit `session.session`: it gives access to an authorized Telegram session.
- Use only your own Telegram account and your own API credentials.
- Follow Telegram and LeoMatch rules when automating actions.

## Лицензия

MIT License.
