import logging
import os
import time

import requests
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

PRAKTIKUM_API = "https://praktikum.yandex.ru"


def parse_homework_status(homework):
    name = homework.get("homework_name")
    if name is None:
        return "Отсутствует имя работы:("
    status = homework.get("status")
    if status is None:
        return "Отсутствует статус работы:("

    if status == "rejected":
        verdict = "К сожалению в работе нашлись ошибки."
    else:
        verdict = (
            "Ревьюеру всё понравилось, можно приступать к следующему уроку."
        )
    return f'У вас проверили работу "{name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    params = {"from_date": current_timestamp}
    headers = {
        "Authorization": f"OAuth {PRAKTIKUM_TOKEN}",
    }
    homework_statuses = requests.get(
        f"{PRAKTIKUM_API}/api/user_api/homework_statuses/",
        params=params,
        headers=headers,
    )
    return homework_statuses.json()


def send_message(message, bot_client):
    logging.info("Посылаю сообщение в Telegram")
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot_client = Bot(token=TELEGRAM_TOKEN)
    logging.debug("Запущен Telegram-бот")
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get("homeworks"):
                send_message(
                    parse_homework_status(new_homework.get("homeworks")[0]),
                    bot_client,
                )
            current_timestamp = new_homework.get(
                "current_date", current_timestamp
            )
            time.sleep(300)

        except Exception as e:
            logging.exception("Бот столкнулся с ошибкой")
            send_message(e, bot_client)
            time.sleep(5)


if __name__ == "__main__":
    main()
