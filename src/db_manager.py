import os
from dotenv import load_dotenv

import psycopg2

load_dotenv()


class DBManager:
    """ Класс для получения информации из базы данных """

    def __init__(self):
        """ Инициализатор """

        self.conn_params = {
            'dbname': os.getenv('HH_DB_NAME'),
            'user': os.getenv('HH_DB_USER'),
            'password': os.getenv('HH_DB_PASSWORD'),
            'host': os.getenv('HH_DB_HOST'),
            'port': os.getenv('HH_DB_PORT', '5432')  # Порт по умолчанию
        }
        self.conn = psycopg2.connect(**self.conn_params)

    def get_companies_and_vacancies_count(self) -> list:
        """ Получает список всех компаний и количество вакансий у каждой компании. """

        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT ec.employer_name, 
                COUNT(v.employer_id) AS vacancies_count 
                FROM employer_company ec 
                LEFT JOIN vacancies v ON ec.employer_id = v.employer_id 
                GROUP BY ec.employer_id, ec.employer_name;
            """)
            rows = cur.fetchall()
            return rows

    def get_all_vacancies(self) -> list:
        """ Получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию. """

        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT employer_company.employer_name,
                vacancies.name,
                vacancies.salary_from,
                vacancies.salary_to,
                vacancies.url
                FROM vacancies INNER JOIN employer_company
                ON vacancies.employer_id = employer_company.employer_id;
            """)
            rows = cur.fetchall()
            return rows

    def get_avg_salary(self) -> tuple:
        """ Получает среднюю зарплату по вакансиям. """

        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT AVG(
                CASE 
                WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL 
                THEN (salary_from + salary_to) / 2 
                WHEN salary_from IS NOT NULL 
                THEN salary_from 
                WHEN salary_to IS NOT NULL 
                THEN salary_to 
                ELSE NULL 
                END
                ) AS average_salary 
                FROM vacancies 
                WHERE 
                salary_from IS NOT NULL 
                OR salary_to IS NOT NULL;
            """)
            result = cur.fetchone()
            return result

    def get_vacancies_with_higher_salary(self) -> list:
        """ Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям. """

        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    name,
                    salary_from,
                    salary_to,
                    url
                FROM vacancies
                WHERE 
                    CASE 
                        WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL 
                        THEN (salary_from + salary_to) / 2 
                        WHEN salary_from IS NOT NULL 
                        THEN salary_from 
                        WHEN salary_to IS NOT NULL 
                        THEN salary_to 
                        ELSE NULL 
                    END > (
                        SELECT AVG(
                            CASE 
                                WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL 
                                THEN (salary_from + salary_to) / 2 
                                WHEN salary_from IS NOT NULL 
                                THEN salary_from 
                                WHEN salary_to IS NOT NULL 
                                THEN salary_to 
                                ELSE NULL 
                            END
                        ) 
                        FROM vacancies 
                        WHERE 
                            salary_from IS NOT NULL 
                            OR salary_to IS NOT NULL
                    )
                AND (salary_from IS NOT NULL OR salary_to IS NOT NULL);
            """)
            rows = cur.fetchall()
            return rows

    def get_vacancies_with_keyword(self, keyword: str) -> list:
        """ Получает список всех вакансий, в названии которых содержатся переданные в метод слова, например python. """  # В методе используется SQL-запрос, выводящий список всех вакансий, в названии которых содержатся переданные в метод слова через оператор LIKE.

        with self.conn.cursor() as cur:
            cur.execute("""
            SELECT name, url
            FROM vacancies
            WHERE name ILIKE %s
            """,
                        (f"%{keyword}%",))
            rows = cur.fetchall()
            return rows
