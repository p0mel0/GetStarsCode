import requests, time, re, os, datetime
from bs4 import BeautifulSoup
from multiprocessing import Queue
from threading import Thread


class Code_spider(object):
    def __init__(self):
        self.urls_file = 'ProjectUrl_stars.txt'  # 存放项目链接的文件
        self.folder = 'F:/PyProject/GetCode_MyStar/projects(stars)/'  # 项目存放目录
        self.headers = {'User-Agent': 'Mozilla/5.0'}
        self.urlCount = 0
        self.q1 = Queue()  # 创建消息队列，存放项目主页的链接
        self.q2 = Queue()  # 创建消息队列，存放下载链接和对应项目名

    # 根据方法名称启动线程
    def work(self, methode_name):
        L = []
        for i in range(50):
            if methode_name == 'get_DownUrl':
                th = Thread(target=self.get_DownUrl, args=(i + 1,))
                th.start()
                L.append(th)
            elif methode_name == 'down_load':
                th = Thread(target=self.down_load, args=(i + 1,))
                th.start()
                L.append(th)
            else:
                exit('方法名称有误，线程终止')
        for th in L:
            th.join()

    # 从文件读取各项目主页链接
    def get_MainUrl(self):
        fp = open(self.urls_file, 'r')
        for url in fp.readlines():
            self.q1.put(url.strip())
        fp.close()
        print("本次将爬取", self.q1.qsize(), "个下载链接")

    # 多线程循环获取项目主页面上的下载链接
    def get_DownUrl(self, n):
        while True:
            try:
                mainUrl = self.q1.get(block=True, timeout=2).strip()
            except:
                # print('爬取不到链接了,%s号线程结束工作' % n)
                break
            response = requests.get(mainUrl, self.headers)
            content = response.text
            soup = BeautifulSoup(content, "html.parser")
            a = soup.find_all('a', class_=re.compile("btn btn-outline get-repo-btn"))  # 获取下载zip的链接
            zip_url = ''
            for k in a:
                zip_url = 'https://github.com' + k['href']
            linkAndFilename = []
            linkAndFilename.append(mainUrl.split('/')[-1])
            linkAndFilename.append(zip_url)
            self.q2.put(linkAndFilename)
            self.urlCount += 1
            print('已爬取%s个下载链接\n' % self.urlCount, end='')

    # 多线程循环执行的下载函数
    def down_load(self, n):
        while True:
            try:
                linkAndFilename = self.q2.get(block=True, timeout=2)
                filename = linkAndFilename[0].strip()
                link = linkAndFilename[1]
            except:
                # print('取不到链接了,%s号线程结束工作' % n)
                break
            # 文件的绝对路径
            abs_filename = self.folder + filename + '.zip'
            # 只下载本地不存在或文件大小为0的链接
            if (not os.path.exists(abs_filename)) or os.path.getsize(abs_filename) == 0:
                with open(abs_filename, 'wb') as code:
                    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "线程%s开始下载：%s\n" % (n, filename),
                          end='')
                    # 若网络情况的变化导致异常，则3s后重新请求，一直循环，直到访问站点成功
                    while True:
                        try:
                            code.write(requests.get(link, self.headers).content)
                            break
                        except:
                            print('%s号线程网络请求发生异常，尝试重新下载...' % n)
                            time.sleep(3)
                    self.urlCount -= 1
                    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "线程%s完成下载：%s,共剩余%s个项目正在下载\n" % (
                        n, filename, self.urlCount), end='')
            else:
                self.urlCount -= 1
                print('%s文件已存在，无需下载，共剩余%s个项目正在下载\n' % (abs_filename, self.urlCount), end='')


if __name__ == '__main__':
    start_time = time.time()

    spider = Code_spider()
    spider.get_MainUrl()
    print('开始爬取下载链接...')
    spider.work('get_DownUrl')
    print('开始下载文件...')
    spider.work('down_load')

    end_time = time.time()
    print("爬取总时间:", end_time - start_time)
