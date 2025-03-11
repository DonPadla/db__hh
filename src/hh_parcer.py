import requests
import logging


class HHParser():
    """ Класс для получени данных о работодателях и подготовки к дальнейшей работе """

    def __init__(self, employer_id):
        """ Инициализация """

        self.employer_id = employer_id
        self.vacancies_url = ""

    def connecting_to_website(self) -> dict:
        """ Подключение к HH.ru """

        response = requests.get(f"https://api.hh.ru/employers/{self.employer_id}")

        employer_id = None
        employer_name = None
        open_vacancies = None

        if response.status_code == 200:
            employer_data = response.json()
            logging.info(f"Подключение к hh.ru по ID {self.employer_id} выполнено успешно.")
            employer_id = employer_data["id"]
            employer_name = employer_data["name"]
            open_vacancies = employer_data["open_vacancies"]
            self.vacancies_url = employer_data["vacancies_url"]

        else:
            logging.warning(f"Пришлось пропустить ID: {self.employer_id}. Возможно такого не существует.")

        return {
            "id": employer_id,
            "name": employer_name,
            "open_vacancies": open_vacancies
        }

    def getting_a_list_of_vacancies(self) -> list:
        """ Получает ссылку от "connecting_to_website". Парсит. Вынимает нужные данные по каждой вакансии. """

        response = requests.get(self.vacancies_url)
        job_list_for_dbmanager = []

        if response.status_code == 200:
            vacancies_data = response.json()
            list_of_vacancies = vacancies_data['items']
            logging.info(f"Подключение к hh.ru по ссылке {self.vacancies_url} выполнено успешно.")

            dict_of_vacancy = {}

            for vacancy in list_of_vacancies:
                dict_of_vacancy['id'] = vacancy['id']
                dict_of_vacancy['name'] = vacancy['name']
                dict_of_vacancy['salary_from'] = (vacancy.get("salary", {}) or {}).get("from")
                dict_of_vacancy['salary_to'] = (vacancy.get("salary", {}) or {}).get("to")
                dict_of_vacancy['city'] = (vacancy.get('address') or {}).get('city', 'null')
                dict_of_vacancy['employer'] = vacancy['employer']['name']
                dict_of_vacancy['url'] = vacancy['alternate_url']
                job_list_for_dbmanager.append(dict_of_vacancy)

        else:
            logging.info(f"Ошибка подключения к hh.ru по ссылке {self.vacancies_url}.")

        return job_list_for_dbmanager
