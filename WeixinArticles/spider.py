import requests
import pymongo
import time
from urllib.parse import urlencode
from requests.exceptions import ConnectionError
from pyquery import PyQuery as pq
base_url = 'https://weixin.sogou.com/weixin?'
headers = {
    'Cookie':
    'IPLOC=CN4403; SUID=4CAA85DB5018910A000000005DB796A5; SUV=1572312742360551; ABTEST=0|1572312750|v1; SNUID=1FF9D6885257C551C5A0626853B0F374; weixinIndexVisited=1; sct=1; JSESSIONID=aaaVlIH8ynu3Ua7VHTs4w; ppinf=5|1572313293|1573522893|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToyNzolRTklOTklODglRTYlOTklOTMlRTYlQjYlOUJ8Y3J0OjEwOjE1NzIzMTMyOTN8cmVmbmljazoyNzolRTklOTklODglRTYlOTklOTMlRTYlQjYlOUJ8dXNlcmlkOjQ0Om85dDJsdUVjM01mcDJPZVFhWE90UXdnMTAyX2dAd2VpeGluLnNvaHUuY29tfA; pprdig=nwscXNp6ohODbh9BaowvQey_13OXW389Ve-Vne39I4j1K_FTiAZUMsKz5mYXtU7Z7YEp9n4HNYCtdU5aN_0EeqhA7oBe9vunvElsAMsPQLOoYSZlY2htQ7FzTjKL5biQL5sGYBSr9EPiPzEsmZr1toKLSoEX4LmzHkgQBXD2SDg; sgid=26-43981093-AV23mM17FxS0ibjB3qzkLibJ4; ppmdig=1572313293000000fbb43066e15a3c33b501624758b7c284',
    'Host':
    'weixin.sogou.com',
    'Upgrade-Insecure-Requests':
    '1',
    'User-Agent':
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}
keyword = '风景'
proxy_pool_url = 'http://127.0.0.1:5000/get'

proxy = None
max_count = 5

client = pymongo.MongoClient('localhost')
db = client['Weixin']


def get_proxy():
    try:
        response = requests.get(proxy_pool_url)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None


def get_html(url, count=1):
    print('Crawling', url)
    print('Try Count', count)
    global proxy
    if count >= max_count:
        print('Tried Too Many Counts')
        return None
    try:
        if proxy:
            proxies = {'http': 'http://' + proxy}
            response = requests.get(url,
                                    allow_redirects=False,
                                    headers=headers,
                                    proxies=proxies)
        else:
            response = requests.get(url,
                                    allow_redirects=False,
                                    headers=headers)
        if response.status_code == 200:
            return response.text
        if response.status_code == 302:
            # Need Proxy
            print('302')
            proxy = get_proxy()
            if proxy:
                print('Using Proxy', proxy)
                return get_html(url)
            else:
                print('Get Proxy Failed')
                # time.sleep(2)
                return None
            pass
    except ConnectionError as e:
        print('ConnectionError', e.args)
        proxy = get_proxy()
        count += 1
        return get_html(url)


def get_index(keyword, page):
    data = {'query': keyword, 'type': 2, 'page': page}
    queries = urlencode(data)
    url = base_url + queries
    html = get_html(url)
    return html


# 获取文章的url
def parse_index(html):
    doc = pq(html)
    items = doc('.news-box .news-list li .txt-box h3 a').items()
    for item in items:
        yield item.attr('href')


# 获取微信的内容
def get_detail(url):
    try:
        if not url.startswith('https://weixin.sogou.com'):
            url = 'https://weixin.sogou.com' + url
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None


# 解析详情页的连接
def parse_detail(html):
    doc = pq(html)
    title = doc('.rich_media_title').text()
    content = doc('.rich_media_content').text()
    date = doc('#publish_time').text()
    mediatext = doc('.rich_media_meta_list .rich_media_meta_text').text()
    nickname = doc('.rich_media_meta_list .rich_media_meta_nickname a').text()
    wechat = doc('#js_profile_qrcode > div > p:nth-child(3) > span').text()
    return {
        'title': title,
        'content': content,
        'date': date,
        'mediatext': mediatext,
        'nickname': nickname,
        'wechat': wechat
    }


def save_to_mongo(data):
    if db['articles'].update({'title': data['title']}, {'$set': data}, True):
        print('Save to Mongo:', data['title'])
    else:
        print('Save to Mongo Failed:', data['title'])


def main():
    for page in range(1, 101):
        html = get_index(keyword, page)
        if html:
            article_urls = parse_index(html)
            for article_url in article_urls:
                # https://weixin.sogou.com
                article_html = get_detail(article_url)
                if article_html:
                    print('article_url', article_url)
                    print('article_html', article_html)
                    article_data = parse_detail(article_html)
                    print(article_data)
                    if article_data:
                        save_to_mongo(article_data)


if __name__ == "__main__":
    main()
