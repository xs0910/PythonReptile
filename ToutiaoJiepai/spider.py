import requests
import time
from urllib.parse import urlencode
from requests.exceptions import RequestException
import random


def get_page_index(offset, keyword):
    data = {
        'aid': 24,
        'app_name': 'web_search',
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'en_qc': 1,
        'cur_tab': 3,
        'from': 'media',
        'pd': 'user',
        'timestamp': time.time()
    }
    url = 'http://www.toutiao.com/api/search/content/?' + urlencode(data)
    headers = {
        'Accept': 'application/json, text/javascript',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'x-requested-with': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
    }
    timeout = random.choice(range(80, 180))
    cookies = {
        'tt_webid': '6752410193911563783',
        'WEATHER_CITY': '北京',
        's_v_web_id': '19c27c191458ee7f6233602c35635966',
        'csrftoken': '63ce749e21d2a8f6031ede0fffe4c0a0'
    }
    try:
        response = requests.get(url,  headers=headers, timeout=timeout)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求索引出错')
        return None


def main():
    html = get_page_index(0, '街拍')
    print(html)


if __name__ == "__main__":
    main()
