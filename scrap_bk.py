import sys
import time
import urllib
import requests
import numpy as np
from bs4 import BeautifulSoup
from openpyxl import Workbook
from collections import OrderedDict


class ScrapyBook(object):
    """scrapy the information of Douban book, including commonly used labels and short comments."""

    def __init__(self, label):
        self.label = label

    def choiceProxy(self):
        with open('Proxys.txt') as f:
            lines = f.read().splitlines()
        proxy_url = np.random.choice(lines)
        proxies = {'https': 'http://'+proxy_url}
        return proxies

    def request(self):
        try_times = 0
        page_num = 0
        books_info = []
        wb = Workbook()
        ws = wb.active
        ws.append(['书名', '评分', 'ISBN', 'URL', '标签', '短评'])
        while (1):
            url = 'https://book.douban.com/tag/' + urllib.parse.quote(self.label) + '?start=' + str(page_num * 20) + '&type=T'
            time.sleep(0.5)
            heads = {}
            heads['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0'
            rep = requests.get(url)
            if rep.status_code != 200:
                while (1):
                    time.sleep(0.5)
                    rep = requests.get(url)
                    if rep.status_code != 200:
                        continue
                    elif rep.status_code == 200:
                        break
            soup = BeautifulSoup(rep.text)
            books = soup.findAll('div', {'class': 'info'})

            if page_num == 51:
                print('完毕！')
                break
            print(url)
            print('--------------------------------------start download %dth page.---------------------------------' % (
                    page_num + 1))
            print('本页有书%d' % len(books) + '本')
            for i, book in enumerate(books):
                try:
                    book_info = OrderedDict()
                    b_url = book.find('a').get('href').strip()
                    b_name = book.find('a').get('title').strip()
                    print('第%d本为%s' % (i + 1, b_name))
                    b_rating = book.find('span', {'class', 'rating_nums'}).text.strip()
                    b_ISBN, b_c_labels, b_comments = self.request_book(b_url)
                    book_info['name'] = b_name
                    book_info['rating'] = b_rating
                    book_info['ISBN'] = b_ISBN
                    book_info['b_url'] = b_url
                    book_info['labels'] = b_c_labels
                    book_info['comments'] = b_comments
                    bcl = '|'.join(s for s in b_c_labels)
                    bc = '|'.join(s for s in b_comments)
                    ws.append([b_name, b_rating, b_ISBN, b_url, bcl, bc])
                    books_info.append(book_info)
                except Exception as e:
                    print('except:', e)
                    wb.save('books.xlsx')
                    continue
            page_num = page_num + 1
            print('downloaded %dth page.' % page_num)
        wb.save('books.xlsx')
        return books_info

    def request_book(self, url):
        time.sleep(0.5)
        rep = requests.get(url)
        if rep.status_code != 200:
            while (1):
                time.sleep(0.5)
                rep = requests.get(url)
                if rep.status_code != 200:
                    continue
                elif rep.status_code == 200:
                    break
        soup = BeautifulSoup(rep.text)

        ISBN = soup.find(id='info').text.strip().split(':')[-1].strip()
        labels = []
        for c in soup.find(id='db-tags-section').findAll('a'):
            labels.append(c.text)
        s = soup.find('div', {'class', 'mod-hd'})
        comments_url = s.findChildren('a')[-1].get('href').strip()
        comments = self.request_comments(comments_url)
        return [ISBN, labels, comments]

    def request_comments(self, url):
        p = 1
        comments = []
        try_times = 0
        print('start scrapy comments')
        while (1):
            c_url = url + 'hot?p=%d' % p
            time.sleep(0.5)
            rep = requests.get(c_url)
            if rep.status_code != 200:
                while (1):
                    time.sleep(0.5)
                    rep = requests.get(url)
                    if rep.status_code != 200:
                        continue
                    elif rep.status_code == 200:
                        break
            soup = BeautifulSoup(rep.text)
            cms = soup.findAll('span', {'class', 'short'})

            if len(cms) < 1 or p > 10:
                break
            print(c_url)
            for c in cms:
                comments.append(c.text.strip())
            p = p + 1
        print('scrapied comments')
        return comments
