# AutoLeoMatch Server Edition by Phoenix

Серверная ветка AutoLeoMatch для непрерывного запуска на VPS или выделенном сервере.
Скрипт анализирует анкеты в Telegram-боте **@leomatchbot** через AI и автоматически отправляет лайк или дизлайк.

Ветка `version_for_server` предназначена для долгой фоновой работы: бот не завершает работу при дневном лимите лайков или временном отсутствии анкет, а ждет и пытается продолжить свайпы позже.

## Что умеет

- Анализирует текст анкеты через OpenAI-compatible Chat Completions API или локальный LM Studio.
- Ставит лайк, если анкета соответствует заданным критериям.
- Пропускает неподходящие и слишком короткие анкеты.
- Пересылает найденные мэтчи и уведомления о лайках в Saved Messages.
- Обрабатывает системные сообщения LeoMatch и продолжает работу без зависания.
- При лимите лайков или отсутствии анкет ждет 1 час, запускает диалог заново и продолжает работу.
- Подходит для запуска в `tmux`, `screen`, `systemd`, Docker Compose или другом process manager на сервере.

## Требования

- Python 3.8+
- Telegram account и API credentials с https://my.telegram.org/apps
- Постоянное интернет-соединение
- Docker и Docker Compose, если нужен запуск в контейнере
- Один из AI-провайдеров:
  - OpenRouter или другой OpenAI-compatible endpoint
  - LM Studio с локально запущенным API

Для серверного режима удобнее использовать OpenRouter или другой внешний OpenAI-compatible endpoint. LM Studio подходит только если модель и локальный API постоянно доступны на том же сервере.

## Установка

```bash
git clone https://github.com/PhoenixInTheDark/AutoLeoMatch.git
cd AutoLeoMatch
git checkout version_for_server
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
LM_STUDIO_API_URL=http://localhost:1234/api/v1/chat
LM_STUDIO_MODEL=mistral-7b-instruct-v0.1

# Параметры работы
MIN_PROFILE_LENGTH=30
RESPONSE_DELAY=1.5
```

`BASE_URL` нужен только если вы используете не стандартный OpenRouter endpoint или совместимый сервис. Для обычного OpenRouter можно удалить эту переменную из `.env` или установить:

```env
BASE_URL=https://openrouter.io/api/v1
```

## Первый запуск и авторизация Telegram

Перед запуском в фоне выполните скрипт один раз в интерактивной SSH-сессии:

```bash
source venv/bin/activate
python dating_bot2.py
```

При первом запуске Telethon попросит войти в Telegram: ввести номер телефона, код подтверждения и, если включена двухфакторная защита, пароль. После успешной авторизации рядом со скриптом появится файл `session.session`.

Сохраните этот файл на сервере. Он нужен для последующих запусков без повторного ввода кода Telegram.

Остановка интерактивного запуска:

```text
Ctrl+C
```

## Запуск на сервере

### Вариант 1: tmux

```bash
tmux new -s autoleomatch
cd /path/to/AutoLeoMatch
source venv/bin/activate
python dating_bot2.py
```

Отключиться от сессии, оставив скрипт работать:

```text
Ctrl+B, затем D
```

Вернуться к логам:

```bash
tmux attach -t autoleomatch
```

### Вариант 2: systemd

Создайте сервис:

```bash
sudo nano /etc/systemd/system/autoleomatch.service
```

Пример unit-файла:

```ini
[Unit]
Description=AutoLeoMatch Server Edition
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

Замените `/path/to/AutoLeoMatch` на реальный путь к проекту, затем включите сервис:

```bash
sudo systemctl daemon-reload
sudo systemctl enable autoleomatch
sudo systemctl start autoleomatch
```

Проверка статуса и логов:

```bash
sudo systemctl status autoleomatch
journalctl -u autoleomatch -f
```

### Вариант 3: Docker Compose

Заполните `.env`, затем соберите образ:

```bash
docker-compose build
```

Если файла `session.session` еще нет, создайте его через одноразовый интерактивный запуск контейнера:

```bash
docker-compose run --rm bot
```

При первом запуске Telethon попросит войти в Telegram: ввести номер телефона, код подтверждения и, если включена двухфакторная защита, пароль. После успешной авторизации рядом с `dating_bot2.py` появится файл `session.session`.

Остановите интерактивный запуск через `Ctrl+C`, затем запустите контейнер в фоне:

```bash
docker-compose up -d
```

Логи контейнера:

```bash
docker-compose logs -f bot
```

Остановка:

```bash
docker-compose down
```

Если у вас установлен новый Docker Compose Plugin, вместо `docker-compose` можно использовать `docker compose`.

Текущий `docker-compose.yml` монтирует каталог проекта в контейнер как `/app`. Поэтому `session.session` хранится на хосте рядом с кодом, не копируется в Docker-образ и переживает пересборку контейнера. `.env` передается в контейнер через `env_file`, а `.dockerignore` не дает секретам и файлам сессии попасть в образ при сборке.

## Поведение в непрерывном режиме

После подключения скрипт слушает сообщения от `BOT_USERNAME` и отвечает лайком или дизлайком.

Если LeoMatch сообщает о дневном лимите лайков или об отсутствии анкет, скрипт:

1. пишет сообщение в лог;
2. ждет 1 час;
3. отправляет `/start`;
4. переходит к следующей анкете;
5. продолжает работу без ручного вмешательства.

Если процесс завершился из-за ошибки окружения, `systemd` перезапустит его автоматически при настройке `Restart=always`. При запуске через Docker Compose перезапуск выполняется политикой `restart: unless-stopped`.

## Критерии отбора

Текущий prompt лайкает только анкеты, где человек:

- ищет отношения;
- хочет длительного общения;
- увлекается содержательными темами вроде IT, музыки или рисования;
- не пишет бессмысленный или явно неподходящий текст.

Анкеты короче `MIN_PROFILE_LENGTH` символов автоматически отклоняются без запроса к модели.

Критерии находятся в `MATCH_PROMPT` внутри `dating_bot2.py`. После изменения prompt лучше проверить поведение на нескольких тестовых анкетах перед длительным запуском.

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

## Лицензия

MIT License.
