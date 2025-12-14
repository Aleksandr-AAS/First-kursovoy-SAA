import json
from unittest.mock import patch, Mock
from requests.exceptions import HTTPError
import pytest
from freezegun import freeze_time
from src.views import analyze_card_transactions
from src.views import get_top_transactions
from src.views import get_exchange
from src.views import get_sp500_stocks
from src.views import get_time_based_greeting


@pytest.fixture
def transactions_list():
    return [
        {
            "Дата операции": "21.03.2019 17:01:38",
            "Дата платежа": "21.03.2019",
            "Номер карты": "22388846849",
            "Статус": "OK",
            "Сумма операции": 190044.51,
            "Валюта операции": "RUB",
            "Сумма платежа": 190044.51,
            "Валюта платежа": "RUB",
            "Кэшбэк": "",
            "Категория": "Переводы",
            "MCC": "",
            "Описание": "Перевод Кредитная карта. ТП 10.2 RUR",
            "Бонусы (включая кэшбэк)": 0,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 190044.51,
        },
        {
            "Дата операции": "21.03.2019 17:01:37",
            "Дата платежа": "21.03.2019",
            "Номер карты": "22388846849",
            "Статус": "OK",
            "Сумма операции": -190044.51,
            "Валюта операции": "RUB",
            "Сумма платежа": -190044.51,
            "Валюта платежа": "RUB",
            "Кэшбэк": "",
            "Категория": "Переводы",
            "MCC": "",
            "Описание": "Перевод Кредитная карта. ТП 10.2 RUR",
            "Бонусы (включая кэшбэк)": 0,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 190044.51,
        },
        {
            "Дата операции": "23.10.2018 12:26:15",
            "Дата платежа": "23.10.2018",
            "Номер карты": "23423561",
            "Статус": "OK",
            "Сумма операции": 177506.03,
            "Валюта операции": "RUB",
            "Сумма платежа": 177506.03,
            "Валюта платежа": "RUB",
            "Кэшбэк": "",
            "Категория": "Переводы",
            "MCC": "",
            "Описание": "Перевод Кредитная карта. ТП 10.2 RUR",
            "Бонусы (включая кэшбэк)": 0,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 177506.03,
        },
        {
            "Дата операции": "23.10.2018 12:26:14",
            "Дата платежа": "23.10.2018",
            "Номер карты": "",
            "Статус": "OK",
            "Сумма операции": -177506.03,
            "Валюта операции": "RUB",
            "Сумма платежа": -177506.03,
            "Валюта платежа": "RUB",
            "Кэшбэк": "",
            "Категория": "Переводы",
            "MCC": "",
            "Описание": "Перевод Кредитная карта. ТП 10.2 RUR",
            "Бонусы (включая кэшбэк)": 0,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 177506.03,
        },
        {
            "Дата операции": "30.12.2021 17:50:17",
            "Дата платежа": "30.12.2021",
            "Номер карты": "*4556",
            "Статус": "OK",
            "Сумма операции": 174000.0,
            "Валюта операции": "RUB",
            "Сумма платежа": 174000.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": "",
            "Категория": "Пополнения",
            "MCC": "",
            "Описание": "Пополнение через Газпромбанк",
            "Бонусы (включая кэшбэк)": 0,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 174000.0,
        },
    ]


def test_analyze_card_transactions(transactions_list):
    res_list = analyze_card_transactions(transactions_list)
    assert res_list == json.dumps(
        [
            {"last_four_digits": "6849", "total_expenses": 380089.02, "cashback": 3800},
            {"last_four_digits": "3561", "total_expenses": 177506.03, "cashback": 1775},
            {"last_four_digits": "4556", "total_expenses": 174000.0, "cashback": 1740},
        ],
        ensure_ascii=False,
        indent=2,
    )
    transactions_list = []
    assert analyze_card_transactions(transactions_list) == "[]"


def test_get_top_transactions(transactions_list):
    res_list = get_top_transactions(transactions_list)
    sorted_trans = sorted(
        transactions_list, key=lambda x: abs(x["Сумма операции"]), reverse=True
    )[:5]
    assert res_list == json.dumps(sorted_trans, ensure_ascii=False, indent=2)
    assert get_top_transactions([]) == "[]"


@patch("requests.get")
def test_get_exchange_success(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "conversion_rates": {
            "USD": 0.13,
            "EUR": 0.11,
        }
    }
    mock_get.return_value = mock_response
    result = get_exchange("ssfd")
    assert result == json.dumps(
        [
            {"currency:": "USD", "rate": round(1 / 0.13, 2)},
            {"currency:": "EUR", "rate": round(1 / 0.11, 2)},
        ],
        indent=2,
    )
    mock_get.assert_called_once()


@patch("requests.get")
def test_get_exchange_fail(mock_get):
    mock_response = Mock()
    http_error_exception = HTTPError("Not Found", response=mock_response)
    mock_response.raise_for_status.side_effect = http_error_exception
    mock_get.return_value = mock_response
    assert get_exchange("sdt") is None
    mock_get.assert_called_once()


def test_get_sp500_stocks():
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.side_effect = [
            {
                "Global Quote": {
                    "01. symbol": "AAPL",
                    "05. price": "310.7400",
                }
            },
            {
                "Global Quote": {
                    "01. symbol": "MSFT",
                    "05. price": "250.7823",
                }
            },
            {
                "Global Quote": {
                    "01. symbol": "GOOGL",
                    "05. price": "210.5410",
                }
            },
            {
                "Global Quote": {
                    "01. symbol": "AMZN",
                    "05. price": "361.3388",
                }
            },
            {
                "Global Quote": {
                    "01. symbol": "TSLA",
                    "05. price": "227.9200",
                }
            },
        ]
        result = get_sp500_stocks("234sxf")
        assert result == json.dumps(
            [
                {"stock": "AAPL", "price": "310.7400"},
                {"stock": "MSFT", "price": "250.7823"},
                {"stock": "GOOGL", "price": "210.5410"},
                {"stock": "AMZN", "price": "361.3388"},
                {"stock": "TSLA", "price": "227.9200"},
            ],
            ensure_ascii=False,
            indent=2,
        )
        assert mock_get.call_count == 5


@freeze_time("2025-04-01 12:00:00")
def test_get_time_based_greeting():
    assert get_time_based_greeting() == "Добрый день!"
