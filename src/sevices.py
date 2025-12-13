import os
import pandas as pd
import json
import logging


current_dir = os.path.dirname(os.path.abspath(__file__))
xls_file_path = os.path.join(current_dir, "../data/operations.xlsx")
xls_file_path_real = os.path.abspath(xls_file_path)  # Это путь до xls

current_dir = os.path.dirname(os.path.abspath(__file__))
rel_file_path = os.path.join(current_dir, "../logs/services.log")
log_file_path = os.path.abspath(rel_file_path)  # Это путь до лог файла

logger = logging.getLogger("services.py")
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


def simple_search(transactions, string_search):
    """Ищет транзакции по строке поиска"""
    results = []
    logger.info("Вызов функции simple_search")
    for transaction in transactions:
        description = transaction.get("Описание", "").lower()
        category = transaction.get("Категория", "").lower()
        search_lower = string_search.lower()
        if search_lower in description or search_lower in category:
            results.append(transaction)

    if len(results) == 0:
        logger.info("По запросу пользователя ничео не найдено")
        return []
    logger.info("Возвращена выборка по запросу пользователя")
    return json.dumps(results, ensure_ascii=False, indent=2)


transactions = read_xls_file(xls_file_path_real)


def main_services(transactions):
    """Главное меню программы простой поиск"""
    menu_text = """
    Привет! Добро пожаловать в программу работы
    с банковскими транзакциями.
    Выберите необходимый пункт меню:
    1. Введите стоку поиска
    2. Выход
    """
    while True:
        print(menu_text)

        try:
            logger.info("Вызов главного меню")
            choice = input("Введите номер пункта меню (1-2): ").strip()
            if choice == "1":
                search = input("Введите строку поиска ").strip().lower()
                print(simple_search(transactions, search))
            elif choice == "2":
                print("Спасибо за использование программы! До свидания!")
                break

            else:
                print("Ошибка: пожалуйста, введите число от 1 до 2")

        except KeyboardInterrupt:
            print("\n\nПрограмма прервана пользователем. До свидания!")
            logger.info("Выход ")
            break
        except Exception as e:
            logger.error("Ошибка вызова главного меню")
            print(f"Произошла ошибка: {e}. Пожалуйста, попробуйте снова.")


# main_services(transactions)
