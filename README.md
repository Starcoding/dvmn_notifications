## dvmn_notifications

Данный бот предназначен для взаимодействия с API DVMN, а имеено позволяет узнавать о статусе проверок уроков.  

# Установка

Для запуска бота необходимо:
- Установить библиотеки `pip install -r requirements.txt`  

Прописать переменные окружения в `.env`: 
- `TELEGRAM_TOKEN` - Секретный ключ телеграм бота  
- `TELEGRAM_CHAT_ID` - Id чата, в который бот будет отправлять оповещения  
- `DVMN_TOKEN`- Секретный ключ сайта [dvmn.org](https://dvmn.org/)  
- `LOGLEVEL` - Переменная указывающая уровень логгирования, например WARNING (Ошибки когда бот "падает"). По умолчанию стоит "INFO"

Запустить бота командой `python bot.py`  

# Деплой
На данный момент бот развёрнут на платформе [heroku.com](https://heroku.com/)
