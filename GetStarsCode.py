# -*- coding: utf-8 -*-
import getopt
import sys
import DownloadByUrls
import requests
from bs4 import BeautifulSoup
import time


# 从用户stars页面爬取各star项目的主页url,并写入文件，如
def getStarredProjects(urls, maxLines):
    hrefs = []
    endOfMatch = False
    for u in urls:
        if endOfMatch:
            break
        try:
            response = requests.get(u, proxies=proxies, headers=headers, timeout=30)
        except:
            print("爬取star项目的主页url异常，请检查网络连接")
            sys.exit()
        content = response.text
        soup = BeautifulSoup(content, "html.parser")
        divs = soup.find_all('div', class_="d-inline-block mb-1")
        for div in divs:
            href = div.find('a')['href']
            hrefs.append(href)
            # 若已达到输入的需求数量，则不再继续往后爬取
            if maxLines != 0 and len(hrefs) >= maxLines:
                endOfMatch = True
                break
    # 将star项目的url记录文本（这里可以用数组记录，但为什么要记录文本？这暂时是为了方便查阅或作其他的爬虫处理）
    num = maxLines if maxLines in range(1, len(hrefs)) else len(hrefs)
    for i in range(num):
        fp.write("https://github.com" + hrefs[i] + "\n")


# 爬取用户的所有stars页面的链接(由于是分页，所以需要遍历所有页)
def getStarredPages(url):
    while True:
        try:
            response = requests.get(url, proxies=proxies, headers=headers, timeout=30)
            content = response.text
            soup = BeautifulSoup(content, "html.parser")
            div = soup.find('div', class_="BtnGroup")
            a = div.find_all('a', class_="btn btn-outline BtnGroup-item")
            for a1 in a:
                if a1.string == 'Next':
                    starredPageUrls.append(a1['href'])
                    url = a1['href']
                    print(url)
            Next = div.find('button', class_="btn btn-outline BtnGroup-item")
            if Next:
                if Next.string == 'Next':
                    break
        except:
            print("爬取分页链接异常，请检查网络连接")
            sys.exit()


def printHelpAndExit():
    print("""usage: python GetStarsCode.py -u <username> [-p <proxy_url>] [-o <output_dir>] [-n <maximum_projects>]
    -u : github用户名
    -p : 代理地址
    -o : 下载到本地的目标目录
    -n : 项目的最大下载数量
Example: python GetStarsCode.py -u "p0mel0" -p "http://127.0.0.1:7890" -o "G:\\temp\\starProject" -n 3""")
    sys.exit()


if __name__ == '__main__':
    username = ''  # 用户名
    proxy = ''  # 代理地址
    outDir = ''  # 下载到本地目录
    limit_num = 0  # 最大项目数，用于star项目数较多的用户，默认为0，即下载所有star项目
    opts = []
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:p:o:n:")
    except getopt.GetoptError:
        printHelpAndExit()
    if len(opts) == 0:
        printHelpAndExit()
    for opt, arg in opts:
        if opt in ("-h", ""):
            printHelpAndExit()
        elif opt == "-u":
            username = arg
        elif opt == "-p":
            proxy = arg
        elif opt == "-o":
            outDir = arg
        elif opt == "-n":
            limit_num = arg

    firstUrl = 'https://github.com/' + username + '?tab=stars'  # 可根据参数过来stars项目，如stars数降序显示：
    fp = open('Url_starProjects.txt', 'w+')
    headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://github.com/'}
    proxies = {'http': proxy, 'https': proxy}
    start_time = time.time()
    # 存放star项目分页链接
    starredPageUrls = [firstUrl]
    print("------------------------------------------")
    print("开始爬取star分页链接")
    print("------------------------------------------")
    getStarredPages(url=firstUrl)

    print("------------------------------------------")
    print("开始爬取star项目主页的url 并写入Url_starProjects.txt")
    print("------------------------------------------")
    getStarredProjects(urls=starredPageUrls, maxLines=int(limit_num))
    print("所有url已写入完成")
    fp.close()

    print("------------------------------------------")
    print('开始爬取下载链接...')
    print("------------------------------------------")
    spider = DownloadByUrls.DownloadByUrls(proxies=proxies, headers=headers, outDir=outDir)
    spider.get_MainUrl()
    spider.work('get_DownUrl')

    print("------------------------------------------")
    print('开始下载...')
    print("------------------------------------------")
    spider.work('down_load')
    end_time = time.time()
    print("下载结束，总耗时:", end_time - start_time, "s")
