from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import NoSuchElementException
import time

# create_driver возвращает объект firefox браузера, созданный
# Selenium, принимая на вход путь до драйвера.
def create_driver(driver_path: str) -> webdriver.Firefox:
    service = Service(driver_path)
    driver = webdriver.Firefox(service=service)
    return driver

# make_query_button_click принимает на вход объект браузера и 
# поисковой запрос, осуществляя переход на первую страницу поисковой
# выдачи при нажатии на кнопку поиска
def make_query_button_click(driver: webdriver.Firefox, query: str) -> None:
    driver.get("https://html.duckduckgo.com/html/")
    driver.find_element("id", "search_form_input_homepage").send_keys(query)
    driver.find_element("id", "search_button_homepage").click()

# more_results_button_click имея объект браузера пытается получить следующую
# страницу поисковой выдачи, нажимая на кнопку внизу страницы ("Next")
def more_results_button_click(driver: webdriver.Firefox) -> bool:
    try:
        driver.find_element("css selector", 'input[type="submit"][value="Next"]').click()
        return True
    except NoSuchElementException:
        return False

# extract_results принимает на вход объект браузера. Используя
# объект браузера, функция извлекает все css атрибуты a.result__url, 
# внутри которых находятся ссылки, ведущие на сайты
def extract_results(driver: webdriver.Firefox) -> list[str]:
    links = driver.find_elements("css selector", "a.result__url")

    return [link.get_attribute("href") for link in links]

# search_by_selenium принимает на вход: 
# driver_path - путь до gecko драйвера
# query - поисковой запрос
# url_limit - лимит по количеству результатов
# delay - задержка между переходами по страницам
# Возвращает множество, содержащее в себе прямые ссылки на сайты.
def search_by_selenium(driver_path: str, query: str, url_limit: int, delay: int) -> set[str]:
    urls = set()
    driver = create_driver(driver_path)
    make_query_button_click(driver, query)

    while len(urls) < url_limit:
        current_urls = extract_results(driver)
        urls.update(current_urls)

        print(f"Количество уникальных результатов: {len(urls)}/{url_limit}")

        if len(urls) >= url_limit:
            break

        if not more_results_button_click(driver):
            print("Кнопка перехода не найдена. Принудительное завершение selenium поиска")
            break

        time.sleep(delay)
    driver.quit()
    return urls