import logging
import os
import traceback
from textwrap import dedent
from time import sleep

import requests
import telegram

bot = telegram.Bot(token=os.environ['TELEGRAM_TOKEN'])
chat_id = os.environ['TELEGRAM_CHAT_ID']
url = 'https://dvmn.org/api/long_polling/'
headers = {'Authorization': f"Token {os.environ['DVMN_TOKEN']}"}
params = {'timestamp': ""}


def send_message(message_text):
    bot.send_message(chat_id=chat_id, text=dedent(message_text))


class ErrorHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        send_message(f'Бот упал с ошибкой:\n{log_entry}')


class InfoHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        send_message(f'{log_entry}')


error_logger = logging.getLogger("ErrorLoger")
error_logger.setLevel(logging.WARNING)
error_logger.addHandler(ErrorHandler())
info_logger = logging.getLogger("InfoLogger")
info_logger.setLevel(logging.INFO)
info_logger.addHandler(InfoHandler())
info_logger.info('Bot started!')
while True:
    try:
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            response_json = response.json()
            response_status = response_json['status']
            if response_status == "found":
                new_attemp = response_json['new_attempts'][0]
                params['timestamp'] = response_json['last_attempt_timestamp']
                is_negative_response = new_attemp['is_negative']
                lesson_title = new_attemp['lesson_title']
                lesson_url = new_attemp['lesson_url']
                if is_negative_response:
                    send_message(f'''
У вас проверили работу «{lesson_title}»‎
К сожалению, в работе нашлись ошибки.
Ссылка на работу: https://dvmn.org{lesson_url}''')
                else:
                    send_message(f'''
У вас проверили работу «{lesson_title}»‎
Преподавателю всё понравилось, можно приступать к следующему уроку!
Ссылка на работу: https://dvmn.org{lesson_url}''')
            else:
                params['timestamp'] = response_json['timestamp_to_request']
        except requests.exceptions.ReadTimeout:
            continue
        except ConnectionError:
            logging.warning('Connection problems!')
            sleep(1800)
            continue
    except Exception as e:
        error_logger.warning(str(e)+str(traceback.format_exc()))
        sleep(1800)