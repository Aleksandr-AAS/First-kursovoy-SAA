import os
import pandas as pd
import json
import logging
from dotenv import load_dotenv
import requests
from datetime import datetime


load_dotenv()
API_KEY = os.getenv("API_KEY")
API_KEY_ACTIONS = os.getenv("API_KEY_ACTIONS")

current_dir = os.path.dirname(os.path.abspath(__file__))
xls_file_path = os.path.join(current_dir, "../data/operations.xlsx")
xls_file_path_real = os.path.abspath(xls_file_path)  # Это путь до xls

current_dir = os.path.dirname(os.path.abspath(__file__))
rel_file_path = os.path.join(current_dir, "../logs/views.log")
log_file_path = os.path.abspath(rel_file_path)  # Это путь до лог файла

logger = logging.getLogger("views.py")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(log_file_path, mode="w", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def read_xls_file(path_to_file):
    """Чтение файла XLS"""
    logger.info("Вызов функции read_xls_file")
    try:
        df = pd.read_excel(path_to_file)
        df = df.fillna("")
        if "description" in df.columns:
            df["description"] = df["description"].astype(str)
        result = df.to_dict("records")
        logger.info("Файл успешно прочитан, данные выведены")
        return result
    except FileNotFoundError:
        logger.error("Неправильный формат файла или файл не найден")
        return []


transactions = read_xls_file(xls_file_path_real)


def analyze_card_transactions(transactions):
    """Анализирует транзакции по картам и возвращает статистику."""
    cards_data = {}
    logger.info("Вызов функции analyze_card_transactions")
    for transaction in transactions:
        card_number = transaction.get("Номер карты")
        if not card_number:
            continue
        amount_key = next((k for k in ["Сумма операции"] if k in transaction), None)
        if not amount_key:
            continue
        amount = transaction[amount_key]
        if isinstance(amount, (int, float)):
            expense_amount = abs(amount) if amount < 0 else amount
        else:
            try:
                expense_amount = float(str(amount).replace(",", "."))
            except ValueError:
                continue
        if card_number not in cards_data:
            last_four = (
                str(card_number)[-4:]
                if len(str(card_number)) >= 4
                else str(card_number)
            )
            cards_data[card_number] = {
                "last_four_digits": last_four,
                "total_expenses": 0.0,
                "cashback": 0.0,
                "card_number": str(card_number),
            }
        cards_data[card_number]["total_expenses"] += expense_amount
        cards_data[card_number]["cashback"] = (
            cards_data[card_number]["total_expenses"] // 100
        )

    # Формируем итоговый результат в нужном формате
    result = []
    for card_info in cards_data.values():
        result.append(
            {
                "last_four_digits": card_info["last_four_digits"],
                "total_expenses": round(card_info["total_expenses"], 2),
                "cashback": int(card_info["cashback"]),
            }
        )
    json_output = json.dumps(result, ensure_ascii=False, indent=2)
    return json_output


# print(analyze_card_transactions(transactions))


def get_top_transactions(transactions):
    """
    Топ-5 транзакций по сумме платежа со статусом - OK
    """
    logger.info("Вызов функции get_top_transactions")
    valid_transactions = []

    for trans in transactions:
        if trans.get("Статус") != "OK":
            continue
        amount = trans.get("Сумма операции")
        if amount is None:
            continue
        try:
            amount_val = float(str(amount).replace(",", "."))
        except (ValueError, TypeError):
            continue
        trans_copy = trans.copy()
        trans_copy["_sort_amount"] = abs(amount_val)
        valid_transactions.append(trans_copy)

    sorted_trans = sorted(
        valid_transactions, key=lambda x: x["_sort_amount"], reverse=True
    )[:5]

    result = []
    for trans in sorted_trans:
        trans_data = {k: v for k, v in trans.items() if k != "_sort_amount"}
        result.append(trans_data)

    return json.dumps(result, ensure_ascii=False, indent=2)


def get_exchange(API_KEY):
    """Получает текущий курс USD и EURO"""
    logger.info("Вызов функции get_exchange")
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/RUB"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        usd_rate = (
            1 / data["conversion_rates"]["USD"]
            if "USD" in data["conversion_rates"]
            else None
        )
        eur_rate = (
            1 / data["conversion_rates"]["EUR"]
            if "EUR" in data["conversion_rates"]
            else None
        )

        return json.dumps(
            [
                {"currency:": "USD", "rate": round(usd_rate, 2)},
                {"currency:": "EUR", "rate": round(eur_rate, 2)},
            ],
            indent=2,
        )

    except requests.exceptions.RequestException as e:
        logger.error("Ошибка функции get_exchange")
        print(f"Ошибка при запросе курса валют: {e}")
        return None


def get_sp500_stocks(api_key):
    """Получение списка акций S&P500"""
    logger.info("Вызов функции get_sp500_stocks")
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]  # 5 компаний
    stocks_data = []
    for symbol in symbols:
        quote_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
        quote_response = requests.get(quote_url)
        data = quote_response.json()

        if "Global Quote" in data:
            stock_info = data["Global Quote"]
            stocks_data.append(
                {
                    "stock": symbol,
                    "price": stock_info.get("05. price"),
                }
            )

    return json.dumps(stocks_data, ensure_ascii=False, indent=2)


def get_time_based_greeting():
    """Время"""
    # Получаем текущий час
    current_hour = datetime.now().hour

    if 5 <= current_hour < 12:
        return "Доброе утро!"
    elif 12 <= current_hour < 17:
        return "Добрый день!"
    elif 17 <= current_hour < 23:
        return "Добрый вечер!"
    else:
        return "Доброй ночи!"


def main_views():
    """Меню"""
    end_res = {
        "greeting": get_time_based_greeting(),
        "cards": json.loads(analyze_card_transactions(transactions)),
        "top_transactions": json.loads(get_top_transactions(transactions)),
        "currency_rates": json.loads(get_exchange(API_KEY)),
        "stock_prices": json.loads(get_sp500_stocks(API_KEY_ACTIONS)),
    }
    print(json.dumps(end_res, ensure_ascii=False, indent=2))


# main_views()
