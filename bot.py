import logging
import os
import traceback
from textwrap import dedent
from time import sleep


import requests
import telegram


def main():
    bot = telegram.Bot(token=os.environ['TELEGRAM_TOKEN'])
    chat_id = os.environ['TELEGRAM_CHAT_ID']
    url = 'https://dvmn.org/api/long_polling/'
    headers = {'Authorization': f"Token {os.environ['DVMN_TOKEN']}"}
    params = {'timestamp': ""}
    log_level = os.environ.get('LOGLEVEL', 'INFO').upper()

    class InfoHandler(logging.Handler):
        def emit(self, record):
            log_entry = self.format(record)
            bot.send_message(chat_id=chat_id, text=dedent(log_entry))

    logger = logging.getLogger("Logger")
    logger.setLevel(log_level)
    logger.addHandler(InfoHandler())
    logger.info('Bot started!')

    while True:
        try:
            response_from_dvmn = requests.get(url, headers=headers, params=params)
            response_from_dvmn.raise_for_status()
            data_from_response = response_from_dvmn.json()
            response_status = data_from_response['status']
            if response_status == "found":
                new_attemp = data_from_response['new_attempts'][0]
                params['timestamp'] = data_from_response['last_attempt_timestamp']
                is_negative_response = new_attemp['is_negative']
                lesson_title = new_attemp['lesson_title']
                lesson_url = new_attemp['lesson_url']
                if is_negative_response:
                    bot.send_message(chat_id=chat_id, text=dedent(f'''\
                    У вас проверили работу «{lesson_title}»
                    К сожалению, в работе нашлись ошибки.
                    Ссылка на работу: {lesson_url}'''))
                else:
                    bot.send_message(chat_id=chat_id, text=dedent(f'''\
                    У вас проверили работу «{lesson_title}»
                    Преподавателю всё понравилось, можно приступать к \
                    следующему уроку!
                    Ссылка на работу: {lesson_url}'''))
            else:
                params['timestamp'] = data_from_response['timestamp_to_request']
        except requests.exceptions.ReadTimeout:
            continue
        except ConnectionError as ce:
            logging.exception(ce)
            sleep(1800)
            continue
        except Exception as e:
            logger.exception(e)
            sleep(1800)


if __name__ == '__main__':
    main()
