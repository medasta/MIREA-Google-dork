import requests
import time


# fetch принимает на вход объект сессии, номер страницы, поисковый запрос,
# список поисковых движков и URL SearXNG. Выполняет поисковый запрос
# и возвращает результаты в виде списка словарей.
def fetch(session: requests.Session, page: int, query: str, engines: list[str], searxng_url: str) -> list[dict]: 
    params = {
        "q": query,
        "format": "json",
        "pageno": page,
        "language": "all",
        "categories": "general",
        "safesearch": 0,
        "engines": ",".join(engines)
    }

    response = session.get(
        searxng_url,
        params=params,
        timeout=45
    )

    if response.status_code != 200:
        return []

    data = response.json()

    return data.get("results", [])


# get_urls принимает результаты SearXNG и извлекает из них
# прямые ссылки на найденные сайты.
def get_urls(results: list[dict]) -> set[str]:
    urls = set()

    for result in results:
        url = result.get("url")

        if url:
            urls.add(url)

    return urls


# search_by_searxng принимает на вход:
# url_limit - лимит по количеству результатов
# query - поисковый запрос
# engines - список поисковых движков SearXNG
# sleep_counter - задержка между запросами
# searxng_url - URL сервиса SearXNG
# Возвращает множество, содержащее прямые ссылки на сайты.
def search_by_searxng(url_limit: int, query: str, engines: list[str], sleep_counter: int, searxng_url: str) -> set[str]:
    session = requests.Session()

    page = 1
    urls = set()

    while len(urls) < url_limit:
        results = fetch(
            session,
            page,
            query,
            engines,
            searxng_url
        )

        if len(results) == 0:
            break

        current_urls = get_urls(results)
        urls.update(current_urls)

        print(f"Количество уникальных результатов: {len(urls)}/{url_limit}")

        if len(urls) >= url_limit:
            break

        page += 1

        time.sleep(sleep_counter)

    session.close()

    return urls