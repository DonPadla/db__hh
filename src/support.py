import logging
import os
from dotenv import load_dotenv

from src.hh_parcer import HHParser
import psycopg2

load_dotenv()


def create_database():
    """ Создание базы данных, если ее нет """

    conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('HH_DB_USER'),
        password=os.getenv('HH_DB_PASSWORD'),
        host=os.getenv('HH_DB_HOST')
    )
    conn.autocommit = True

    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", ('hh_db',))
    exists = cursor.fetchone()

    if not exists:
        cursor.execute(f'CREATE DATABASE hh_db')
        logging.info('База данных создана')

    else:
        logging.info('База данных уже существует')

    cursor.close()
    conn.close()


def create_table_employer_company():
    """ Создание таблицы работодатели """

    conn = psycopg2.connect(
        dbname=os.getenv('HH_DB_NAME'),
        user=os.getenv('HH_DB_USER'),
        password=os.getenv('HH_DB_PASSWORD'),
        host=os.getenv('HH_DB_HOST')
    )

    cursor = conn.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS employer_company (
    employer_id INTEGER PRIMARY KEY,
    employer_name VARCHAR(100) NOT NULL,
    open_vacancies INTEGER
    );    
    """

    cursor.execute(create_table_query)
    conn.commit()

    cursor.close()
    conn.close()


def create_table_vacancies():
    """ Создание таблицы с вакансиями """

    conn = psycopg2.connect(
        dbname=os.getenv('HH_DB_NAME'),
        user=os.getenv('HH_DB_USER'),
        password=os.getenv('HH_DB_PASSWORD'),
        host=os.getenv('HH_DB_HOST')
    )

    cursor = conn.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS vacancies (
    vacancy_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    salary_from REAL,
    salary_to REAL,
    city VARCHAR(100),
    employer_name VARCHAR(100),
    employer_id INTEGER,
    FOREIGN KEY (employer_id) REFERENCES employer_company(employer_id),
    url TEXT
    );
    """

    cursor.execute(create_table_query)
    conn.commit()

    cursor.close()
    conn.close()


def filling_in_the_table_employer_company(employer_id_list):
    """ Заполнение таблицы employer_company """

    conn = psycopg2.connect(
        dbname=os.getenv('HH_DB_NAME'),
        user=os.getenv('HH_DB_USER'),
        password=os.getenv('HH_DB_PASSWORD'),
        host=os.getenv('HH_DB_HOST')
    )
    cursor = conn.cursor()

    for employer_id in employer_id_list:

        try:
            parser = HHParser(employer_id=employer_id)
            employer_data = parser.connecting_to_website()
            employer_id = employer_data.get('id')
            name = employer_data.get('name')
            open_vacancies = employer_data.get('open_vacancies')

            insert_query = ("INSERT INTO employer_company (employer_id, employer_name, open_vacancies) "
                            "VALUES (%s, %s, %s) "
                            "ON CONFLICT (employer_id) DO NOTHING  -- Если есть UNIQUE/PRIMARY KEY")
            cursor.execute(insert_query, (employer_id, name, open_vacancies))

        except Exception:
            continue

    conn.commit()
    logging.info("Данные добавлены в таблицу employer_company")

    cursor.close()
    conn.close()


def filling_in_the_table_vacancies(employer_id_list):
    conn = psycopg2.connect(
        dbname=os.getenv('HH_DB_NAME'),
        user=os.getenv('HH_DB_USER'),
        password=os.getenv('HH_DB_PASSWORD'),
        host=os.getenv('HH_DB_HOST')
    )
    cursor = conn.cursor()

    for employer_id in employer_id_list:

        try:
            parser = HHParser(employer_id=employer_id)
            parser.connecting_to_website()
            vacancies_data = parser.getting_a_list_of_vacancies()

            for vacancy in vacancies_data:
                vacancy_id = vacancy.get('id')
                vacancy_name = vacancy.get('name')
                vacancy_salary_from = vacancy.get('salary_from')
                vacancy_salary_to = vacancy.get('salary_to')
                vacancy_city = vacancy.get('city')
                vacancy_employer_name = vacancy.get('employer')
                vacancy_employer_id = employer_id
                vacancy_url = vacancy.get('url')

                insert_query = ("""INSERT INTO  vacancies(
                                vacancy_id,
                                name,
                                salary_from,
                                salary_to,
                                city,
                                employer_name,
                                employer_id,
                                url)"""
                                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "
                                "ON CONFLICT (vacancy_id) DO NOTHING")

                cursor.execute(
                    insert_query,
                    (
                        vacancy_id,
                        vacancy_name,
                        vacancy_salary_from,
                        vacancy_salary_to,
                        vacancy_city,
                        vacancy_employer_name,
                        vacancy_employer_id,
                        vacancy_url
                    )
                )

        except Exception:
            continue

    conn.commit()
    logging.info("Данные добавлены в таблицу vacancies")

    cursor.close()
    conn.close()


def unpacking_employer_list(employer_list):
    """ Распаковка списка работодателей для человекочитаемости """

    for row in employer_list:
        print(f"Имя компании: {row[0]}, количество открытых вакансий: {row[1]}")


def unpacing_vacancies_list(vacancies_list):
    """ Распаковка списка вакансий для человекочитаемости """

    for row in vacancies_list:
        print(f"Компания: {row[0]}, вакансия: {row[1]}, з.п. от: {row[2]} до {row[3]}, ссылка: {row[4]}")


def unpacing_big_salary(vacancies_list):
    """ Распаковка списка вакансий с зп выше средней """

    for row in vacancies_list:
        print(f"Вакансия: {row[0]}, з.п. от: {row[1]} до {row[2]}, ссылка: {row[3]}")


def unpacing_search(search_list):
    """ Распаковка списка вакансий """

    if not search_list:
        print("Ничего не нашлось:(")

    else:

        for row in search_list:
            vacancy_name = row[0] if row[0] else "Не указано"
            vacancy_url = row[1] if row[1] else "Ссылка отсутствует"
            print(f"Вакансия: {vacancy_name}, ссылка: {vacancy_url}")
