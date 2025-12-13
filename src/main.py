import os
from src.views import main_views
from src.sevices import main_services
from src.sevices import read_xls_file
from src.reports import read_xls_file_df
from src.reports import get_spending_last_three_months

current_dir = os.path.dirname(os.path.abspath(__file__))
xls_file_path = os.path.join(current_dir, "../data/operations.xlsx")
xls_file_path_real = os.path.abspath(xls_file_path)  # Это путь до xls


transactions = read_xls_file(xls_file_path_real)
transactions_df = read_xls_file_df(xls_file_path_real)


def main_menu():
    """Главное меню Курсовой"""
    menu_text = """
    Привет! Добро пожаловать в КУРСОВОЙ.
    Выберите необходимый пункт меню:
    1. Веб страницы - Главная
    2. Сервисы - Простой поиск
    3. Отчеты - траты по категориям
    4. Выход
    """

    while True:
        print(menu_text)

        try:
            choice = input("Введите номер пункта меню (1-4): ").strip()
            if choice == "1":
                print("Веб страницы - Главная")
                main_views()

            elif choice == "2":
                print("Сервисы - Простой поиск")
                main_services(transactions)

            elif choice == "3":
                print("Отчеты  - траты по категориям")
                print(get_spending_last_three_months(transactions_df, "Супермаркеты", "05.04.2019"))

            elif choice == "4":
                print("Спасибо за использование программы! До свидания!")
                break

            else:
                print("Ошибка: пожалуйста, введите число от 1 до 4")

        except KeyboardInterrupt:
            print("\n\nПрограмма прервана пользователем. До свидания!")
            break
        except Exception as e:
            print(f"Произошла ошибка: {e}. Пожалуйста, попробуйте снова.")


main_menu()
