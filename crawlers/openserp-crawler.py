import requests
import time


# make_query принимает на вход объект сессии, поисковой запрос,
# поисковые движки, смещение результатов и URL OpenSERP. Выполняет
# поисковый запрос и возвращает ответ OpenSERP в виде словаря.
def make_query(session: requests.Session, query: str, engines: list[str], start: int, openserp_url: str) -> dict:
    params = {
        "text": query,
        "engines": ",".join(engines),
        "limit": 10,
        "start": start
    }

    response = session.get(openserp_url, params=params)
    response.raise_for_status()

    return response.json()


# extract_results принимает ответ OpenSERP и извлекает из него
# прямые ссылки на найденные сайты.
def extract_results(response: dict) -> list[str]:
    urls = []
    results = response.get("results", [])

    for result in results:
        url = result.get("url")

        if url:
            urls.append(url)

    return urls


# search_by_openserp принимает на вход:
# url_limit - лимит по количеству результатов
# query - поисковый запрос
# engines - поисковые движки OpenSERP
# openserp_url - URL сервиса OpenSERP
# Возвращает множество, содержащее прямые ссылки на сайты.
def search_by_openserp(url_limit: int, query: str, engines: list[str], openserp_url: str, delay: int) -> set[str]:
    urls = set()
    start = 0

    session = requests.Session()

    while len(urls) < url_limit:
        response = make_query(session, query, engines, start, openserp_url)

        current_urls = extract_results(response)
        urls.update(current_urls)

        print(f"Количество уникальных результатов: {len(urls)}/{url_limit}")

        if len(urls) >= url_limit:
            break

        pagination = response.get("pagination", {})

        if not pagination.get("has_more"):
            break

        start = pagination.get("next_start")

        if start is None:
            break
        time.sleep(delay)
    return urls