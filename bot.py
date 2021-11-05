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
    LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()

    class InfoHandler(logging.Handler):
        def emit(self, record):
            log_entry = self.format(record)
            bot.send_message(chat_id=chat_id, text=dedent(f'{log_entry}'))


    logger = logging.getLogger("Logger")
    logger.setLevel(LOGLEVEL)
    logger.addHandler(InfoHandler())
    logger.info('Bot started!')


    while True:
        try:
            0/0
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            response = response.json()
            response_status = response['status']
            if response_status == "found":
                new_attemp = response['new_attempts'][0]
                params['timestamp'] = response['last_attempt_timestamp']
                is_negative_response = new_attemp['is_negative']
                lesson_title = new_attemp['lesson_title']
                lesson_url = new_attemp['lesson_url']
                if is_negative_response:
                    bot.send_message(chat_id=chat_id, text=dedent(f'''
У вас проверили работу «{lesson_title}»‎
К сожалению, в работе нашлись ошибки.
Ссылка на работу: https://dvmn.org{lesson_url}'''))
                else:
                    bot.send_message(chat_id=chat_id, text=dedent(f'''
У вас проверили работу «{lesson_title}»‎
Преподавателю всё понравилось, можно приступать к следующему уроку!
Ссылка на работу: https://dvmn.org{lesson_url}'''))
            else:
                params['timestamp'] = response['timestamp_to_request']
        except requests.exceptions.ReadTimeout:
            continue
        except ConnectionError:
            logging.warning('Connection problems!')
            sleep(1800)
            continue
        except Exception as e:
            logger.warning(f'Бот упал с ошибкой: \n{str(e)+str(traceback.format_exc())}')
            sleep(1800)


if __name__ == '__main__':
    main()