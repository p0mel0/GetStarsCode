# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import time


# 从搜索结果爬取各项目主页url,写入文件
def getProject(urls):
    for url in urls:
        response = requests.get(url, headers=headers)
        content = response.text
        soup = BeautifulSoup(content, "html.parser")
        divs = soup.find_all('div', class_="d-inline-block mb-1")
        for div in divs:
            a = div.find('a')
            href = a['href']
            print(href)
            fp.write("https://github.com" + href + "\n")


# 爬取用户的所有stars页面的链接
def getAllStarsPages(url):
    while True:
        try:
            response = requests.get(url, headers=headers)
            content = response.text
            soup = BeautifulSoup(content, "html.parser")
            div = soup.find('div', class_="BtnGroup")
            a = div.find_all('a', class_="btn btn-outline BtnGroup-item")
            for a1 in a:
                if a1.string == 'Next':
                    mystarts_pages.append(a1['href'])
                    url = a1['href']
                    print(url)
            Next = div.find('button', class_="btn btn-outline BtnGroup-item")
            if Next:
                if Next.string == 'Next':
                    break
        except:
            time.sleep(3)


if __name__ == '__main__':
    username = 'p0m1012'  # 用户名

    url = 'https://github.com/' + username + '?tab=stars&direction=desc&sort=stars'  # stars页面按starts数降序显示
    fp = open('ProjectUrl_stars.txt', 'w+')
    headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://github.com/'}
    mystarts_pages = []
    mystarts_pages.append(url)

    getAllStarsPages(url)
    getProject(mystarts_pages)
    fp.close()
