import os
import pandas as pd
from datetime import datetime
from typing import Optional, Union
import logging


current_dir = os.path.dirname(os.path.abspath(__file__))
xls_file_path = os.path.join(current_dir, "../data/operations.xlsx")
xls_file_path_real = os.path.abspath(xls_file_path)  # Это путь до xls

current_dir = os.path.dirname(os.path.abspath(__file__))
rel_file_path = os.path.join(current_dir, "../logs/reports.log")
log_file_path = os.path.abspath(rel_file_path)  # Это путь до лог файла

logger = logging.getLogger("reports.py")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(log_file_path, mode="w", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def read_xls_file_df(path_to_file):
    """Чтение файла XLS"""
    logger.info("Вызов функции read_xls_file_df")
    try:
        df = pd.read_excel(path_to_file)
        df = df.fillna("")
        if "description" in df.columns:
            df["description"] = df["description"].astype(str)
        result = df
        logger.info("Файл успешно прочитан, данные выведены")
        return result
    except FileNotFoundError:
        logger.error("Неправильный формат файла или файл не найден")
        return []


transactions_df = read_xls_file_df(xls_file_path_real)


def get_spending_last_three_months(
    transactions_df: pd.DataFrame,
    category: str,
    target_date: Optional[Union[str, datetime]] = None,
) -> pd.DataFrame:
    """Что то там за последние 3 мксяца """
    logger.info("Вызов функции get_spending_last_three_months")
    df = transactions_df.copy()

    possible_date_cols = [
        "Дата операции",
        "date",
        "Date",
        "дата",
        "Дата",
        "transaction_date",
        "Date/Time",
    ]
    possible_category_cols = [
        "Супермаркеты",
        "category",
        "Category",
        "категория",
        "Категория",
        "Category Name",
    ]
    possible_amount_cols = [
        "Сумма операции",
        "amount",
        "Amount",
        "сумма",
        "Сумма",
        "transaction_amount",
        "Сумма платежа",
    ]

    for col in possible_date_cols:
        if col in transactions_df.columns:
            date_col = col
            break

    for col in possible_category_cols:
        if col in transactions_df.columns:
            category_col = col
            break

    for col in possible_amount_cols:
        if col in transactions_df.columns:
            amount_col = col
            break

    df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")

    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    if not pd.api.types.is_numeric_dtype(df[amount_col]):
        df[amount_col] = pd.to_numeric(df[amount_col], errors="coerce")

    if target_date is None:
        target_date = datetime.now()
    elif isinstance(target_date, str):
        target_date = pd.to_datetime(target_date)

    start_date = target_date - pd.DateOffset(months=3)

    mask = (
        (df[date_col] >= start_date)
        & (df[date_col] <= target_date)
        & (df[category_col] == category)
    )

    filtered_df = df[mask].copy()

    filtered_df = filtered_df.sort_values(date_col)

    return filtered_df


print(get_spending_last_three_months(transactions_df, "Супермаркеты", "05.04.2019"))
