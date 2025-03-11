from src.config import employer_id_list
from src.db_manager import DBManager
from src.support import create_database, create_table_employer_company, create_table_vacancies, \
    filling_in_the_table_employer_company, filling_in_the_table_vacancies, unpacking_employer_list, \
    unpacing_vacancies_list, unpacing_big_salary, unpacing_search


create_database()
create_table_employer_company()
create_table_vacancies()
print("""Здравствувйте.
База данных уже создана.
Таблицы тоже, их осталось только заполнить.
В 'config.py' есть список вакансий, которые старательно подбирались,
но если захочешь добавить или поменять, я не сильно обижусь)""")
filling_in_the_table_employer_company(employer_id_list)
filling_in_the_table_vacancies(employer_id_list)


def main():
    """ Функция взаимодействия с пользователем """


    while True:
        work_with_db = input("""
        1. Посмотреть список работодателей.
        2. Посмотреть список вакансий.
        3. Узнать среднюю зарплату по всем вакансиям.
        4. Посмотреть вакансии с зарплатой выше средней.
        5. Найти вакансии по ключевому слову.
        """)

        if work_with_db == "1":
            unpacking_employer_list(DBManager().get_companies_and_vacancies_count())

        elif work_with_db == "2":
            unpacing_vacancies_list(DBManager().get_all_vacancies())

        elif work_with_db == "3":
            print(round(*(DBManager().get_avg_salary())))

        elif work_with_db == "4":
            unpacing_big_salary(DBManager().get_vacancies_with_higher_salary())

        elif work_with_db == "5":
            unpacing_search(DBManager().get_vacancies_with_keyword(input("Или назовете слово целиком?\n")))

        else:
            print("Я ухожу...")
            break


main()
