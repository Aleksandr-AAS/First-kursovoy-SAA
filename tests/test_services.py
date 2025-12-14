from unittest.mock import patch
import pandas as pd
import pytest
import numpy as np
import json
from src.sevices import read_xls_file, simple_search, main_services


@pytest.fixture
def transactions_list():
    return pd.DataFrame(
        [
            {
                "id": 650703.0,
                "state": np.nan,
                "date": "2023-09-05T11:30:32Z",
                "amount": 16210.0,
                "currency_name": "Sol",
                "currency_code": "PEN",
                "from": "Счет 58803664561298323391",
                "to": "Счет 39745660563456619397",
                "description": 252,
            },
            {
                "id": 3598919.0,
                "state": "EXECUTED",
                "date": "2020-12-06T23:00:58Z",
                "amount": 29740.0,
                "currency_name": np.nan,
                "currency_code": "COP",
                "from": "Discover 3172601889670065",
                "to": "Discover 0720428384694643",
                "description": np.nan,
            },
            {
                "id": 593027.0,
                "state": "CANCELED",
                "date": "2023-07-22T05:02:01Z",
                "amount": 30368.0,
                "currency_name": "Shilling",
                "currency_code": "TZS",
                "from": "Visa 1959232722494097",
                "to": "Visa 6804119550473710",
                "description": "Перевод с карты на карту",
            },
        ]
    )


@pytest.fixture
def transactions_list1():
    return pd.DataFrame(
        [
            {
                "id": 650703.0,
                "state": np.nan,
                "date": "2023-09-05T11:30:32Z",
                "amount": 16210.0,
                "currency_name": "Sol",
                "currency_code": "PEN",
                "from": "Счет 58803664561298323391",
                "to": "Счет 39745660563456619397",
                "Описание": 252,
            },
            {
                "id": 3598919.0,
                "state": "EXECUTED",
                "date": "2020-12-06T23:00:58Z",
                "amount": 29740.0,
                "currency_name": np.nan,
                "currency_code": "COP",
                "from": "Discover 3172601889670065",
                "to": "Discover 0720428384694643",
                "Описание": np.nan,
                "Категория": "Перевод",
            },
            {
                "id": 593027.0,
                "state": "CANCELED",
                "date": "2023-07-22T05:02:01Z",
                "amount": 30368.0,
                "currency_name": "Shilling",
                "currency_code": "TZS",
                "from": "Visa 1959232722494097",
                "to": "Visa 6804119550473710",
                "Описание": "Перевод с карты на карту",
                "Категория": "Чтонибудь",
            },
        ]
    )


@patch("pandas.read_excel")
def test_read_xls_file(mock_read_excel, transactions_list):
    mock_read_excel.return_value = transactions_list
    result = read_xls_file("TEST.xlsx")
    transactions_list = transactions_list.fillna("")
    transactions_list["description"] = transactions_list["description"].astype(str)
    assert result == transactions_list.to_dict("records")
    mock_read_excel.assert_called_once_with("TEST.xlsx")


def test_simple_search(transactions_list1):
    transactions_list1 = transactions_list1.fillna("")
    transactions_list1["Описание"] = transactions_list1["Описание"].astype(str)
    transactions_list1["Категория"] = transactions_list1["Категория"].astype(str)
    transactions_list1 = transactions_list1.to_dict("records")
    result = simple_search(transactions_list1, "Перевод")
    exp = [transactions_list1[1], transactions_list1[2]]
    assert result == json.dumps(exp, ensure_ascii=False, indent=2)
    result = simple_search(transactions_list1, "ЧТОТОНЕСУЩЕСТВУЮЩЕЕ")
    exp = []
    assert result == exp


def test_main_services_exit():
    """Базовый тест выхода из меню"""
    with patch('builtins.input', return_value='2'):
        with patch('builtins.print') as mock_print:
            main_services([])
            mock_print.assert_any_call("Спасибо за использование программы! До свидания!")
