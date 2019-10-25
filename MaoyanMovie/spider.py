import requests
from requests.exceptions import RequestException
import re


def get_one_page(url):
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None


def parse_one_page(html):
    pattern = re.compile(
        '<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?name"><a' +
        '.*?>(.*?)</a>.*?star">(.*?)</p>.*?releasetime">(.*?)</p>' +
        '.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>', re.S)
    items = re.findall(pattern, html)
    print(items)


def main():
    url = 'http://maoyan.com/board/4?'
    html = get_one_page(url)
    parse_one_page(html)


if __name__ == "__main__":
    main()
