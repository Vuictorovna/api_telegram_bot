import logging
import os
import time

import requests
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

PRAKTIKUM_API = "https://praktikum.yandex.ru"


def parse_homework_status(homework):
    name = homework.get("homework_name")
    if name is None:
        raise Exception("Отсутствует имя работы:(")

    status = homework.get("status")
    if status is None:
        raise Exception("Отсутствует статус работы:(")

    if status == "rejected":
        verdict = "К сожалению в работе нашлись ошибки."
    elif status == "approved":
        verdict = (
            "Ревьюеру всё понравилось, можно приступать к следующему уроку."
        )
    elif status == "reviewing":
        verdict = "Ваша работа всё ещё проверяется"
    else:
        raise Exception(f"Неизвестный статус: {status}")

    return f'У вас проверили работу "{name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    params = {"from_date": current_timestamp}
    headers = {
        "Authorization": f"OAuth {PRAKTIKUM_TOKEN}",
    }
    try:
        homework_statuses = requests.get(
            f"{PRAKTIKUM_API}/api/user_api/homework_statuses/",
            params=params,
            headers=headers,
        )
    except requests.exceptions.HTTPError:
        logger.exception("Проблемы с соединением с сервером")
        raise Exception("Не получилось узнать статус вашего домашнего задания")

    return homework_statuses.json()


def send_message(message, bot_client):
    logger.info("Посылаю сообщение в Telegram")
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot_client = Bot(token=TELEGRAM_TOKEN)
    logger.debug("Запущен Telegram-бот")
    current_timestamp = int(time.time())

    while True:
        try:
            new_homeworks = get_homework_statuses(current_timestamp)
            homeworks = new_homeworks.get("homeworks")
            if homeworks:
                send_message(
                    parse_homework_status(homeworks[0]),
                    bot_client,
                )
            current_timestamp = new_homeworks.get(
                "current_date", current_timestamp
            )
            time.sleep(300)

        except Exception as e:
            logger.exception("Бот столкнулся с ошибкой")
            send_message(e, bot_client)
            time.sleep(5)


if __name__ == "__main__":
    main()
