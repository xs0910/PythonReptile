from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
from config import *
import re
import pymongo

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

browser = webdriver.PhantomJS(
    service_args=SERVICE_ARGS)  # 使用PhantomJS,这样不用打开浏览器,整个程序在后台运行
wait = WebDriverWait(browser, 10)

browser.set_window_size(1400, 900)


# 淘宝页搜索
def search():
    print('正在搜索')
    # 判断是否加载成功
    try:
        browser.get('https://www.taobao.com')
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#q")))
        submit = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR,
                 "#J_TSearchForm > div.search-button > button")))
        input.send_keys(KEYWORD)
        submit.click()
        total = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 '#mainsrp-pager > div > div > div > div.total')))
        get_products()
        return total.text
    except TimeoutException:
        return search()


# 输入页码数,点击确定跳转翻页
def next_page(page_number):
    print('正在翻页', page_number)
    try:
        input = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 "#mainsrp-pager > div > div > div > div.form > input")))
        submit = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                "#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit"
            )))
        input.clear()
        input.send_keys(page_number)
        submit.click()
        wait.until(
            EC.text_to_be_present_in_element((
                By.CSS_SELECTOR,
                "#mainsrp-pager > div > div > div > ul > li.item.active > span"
            ), str(page_number)))
        get_products()
    except TimeoutException:
        next_page(page_number)


# 获取调用页的商品信息
def get_products():
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#mainsrp-itemlist .items .item')))
    html = browser.page_source
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('src'),
            'price': item.find('.price').text(),
            'deal': item.find('.deal-cnt').text()[:-3],
            'title': item.find('.title').text(),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text()
        }
        save_to_mongo(product)


# 保存数据的方法
def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('存储到MongoDB成功', result)
    except Exception:
        print('存储到MongoDB错误', result)


def main():
    try:
        total = search()
        total = int(re.compile('(\d+)').search(total).group(1))
        for i in range(2, total + 1):
            next_page(i)
    except Exception:
        print('出错啦')
    finally:
        browser.close()


if __name__ == "__main__":
    main()
