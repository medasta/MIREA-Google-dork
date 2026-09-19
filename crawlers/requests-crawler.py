import requests
from lxml import html
import time


# parse_results принимает страницу поисковой выдачи и извлекает из неё
# прямые ссылки на найденные сайты.
def parse_results(page) -> list[str]:
    urls = []

    result_blocks = page.xpath("//div[contains(@class, 'result__body')]")

    for block in result_blocks:
        url = block.xpath(
            ".//h2[@class='result__title']"
            "//a[@class='result__a']/@href"
        )

        if url:
            urls.append(url[0].strip())

    return urls


# get_next_page принимает страницу поисковой выдачи и текущее смещение.
# Возвращает данные для перехода на следующую страницу или None,
# если следующая страница не найдена.
def get_next_page(page, current_offset: int) -> dict | None:
    forms = page.xpath("//div[contains(@class, 'nav-link')]/form")

    for form in forms:
        data = {}
        input_fields = form.xpath(".//input[@type='hidden']")

        for input_field in input_fields:
            name = input_field.get("name")
            value = input_field.get("value")

            if name:
                data[name] = value

        next_offset = data.get("s")

        if not next_offset:
            continue

        if int(next_offset) > current_offset:
            return data

    return None


# search_by_requests принимает на вход:
# query - поисковый запрос
# url_limit - лимит по количеству результатов
# static_url - URL поисковой системы
# sleep_counter - задержка между запросами
# headers - HTTP-заголовки
# Возвращает множество, содержащее прямые ссылки на сайты.
def search_by_requests(query: str, url_limit: int, static_url: str, sleep_counter: int, headers: dict) -> set[str]:
    session = requests.Session()
    session.headers.update(headers)

    urls = set()
    seen_pages = set()
    current_offset = 0

    response = session.post(
        static_url,
        data={"q": query},
        timeout=10
    )

    if "challenge-form" in response.text:
        return urls

    while len(urls) < url_limit:
        page = html.fromstring(response.text)
        current_urls = parse_results(page)

        urls.update(current_urls)

        print(f"Количество уникальных результатов: {len(urls)}/{url_limit}")

        if len(urls) >= url_limit:
            break

        next_page = get_next_page(page, current_offset)

        if not next_page:
            break

        next_offset = int(next_page["s"])

        if next_offset in seen_pages:
            break

        seen_pages.add(next_offset)
        current_offset = next_offset

        time.sleep(sleep_counter)

        response = session.post(
            static_url,
            data=next_page,
            timeout=10
        )

        if "challenge-form" in response.text:
            break

    session.close()

    return urls