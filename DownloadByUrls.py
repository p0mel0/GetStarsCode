import requests, time, re, os, datetime
from bs4 import BeautifulSoup
from multiprocessing import Queue
from threading import Thread


class DownloadByUrls(object):
    def __init__(self, proxies, outDir, headers):
        self.urls_file = 'Url_starProjects.txt'  # 存放项目链接的文件
        self.folder = outDir  # 项目存放目录（需修改）
        self.headers = headers
        self.proxies = proxies
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

    # 获取项目主页面上的下载链接
    def get_DownUrl(self, n):
        while True:
            try:
                mainUrl = self.q1.get(block=True, timeout=2).strip()
            except:
                # print('爬取不到链接了,%s号线程结束工作' % n)
                break
            response = requests.get(mainUrl, proxies=self.proxies, headers=self.headers, timeout=30)
            content = response.text
            soup = BeautifulSoup(content, "html.parser")
            # 获取下载zip的链接
            summary = soup.find('summary', attrs={"title": "Switch branches or tags"})
            branch = summary.find('span', class_=re.compile("css-truncate-target")).text
            zip_url = mainUrl + "/archive/refs/heads/" + branch + ".zip"

            linkAndFilename = [mainUrl.split('/')[-1], zip_url]
            self.q2.put(linkAndFilename)
            self.urlCount += 1
            print('已爬取%s个下载链接\n' % self.urlCount, end='')

    # 下载函数
    def down_load(self, n, proxies=None):
        while True:
            try:
                linkAndFilename = self.q2.get(block=True, timeout=2)
                filename = linkAndFilename[0].strip()
                link = linkAndFilename[1]
            except:
                # print('取不到链接了,%s号线程结束工作' % n)
                break
            # 文件的绝对路径，若未设置输出目录，则默认下载到当前目录
            if self.folder != '':
                abs_filename = self.folder + "\\" + filename + '.zip'
            else:
                abs_filename = filename + '.zip'

            # 只下载本地不存在或文件大小为0的链接
            if (not os.path.exists(abs_filename)) or os.path.getsize(abs_filename) == 0:
                with open(abs_filename, 'wb') as code:
                    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "线程%s开始下载：%s\n" % (n, filename),
                          end='')
                    errorCount = 0
                    # 若网络情况的变化导致异常，则3s后重新请求，共重试3次
                    while True:
                        if errorCount > 3:
                            break
                        try:
                            print(link)
                            code.write(requests.get(link, proxies=self.proxies, headers=self.headers).content)
                            break
                        except:
                            errorCount += 1
                            print('%s号线程网络请求发生异常，尝试重新下载...' % n)
                            time.sleep(3)
                    self.urlCount -= 1
                    if errorCount > 3:
                        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "线程%s下载失败：%s,共剩余%s个项目正在下载\n" % (
                            n, filename, self.urlCount), end='')
                    else:
                        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "线程%s完成下载：%s,共剩余%s个项目正在下载\n" % (
                            n, filename, self.urlCount), end='')
            else:
                self.urlCount -= 1
                print('%s文件已存在，无需下载，共剩余%s个项目正在下载\n' % (abs_filename, self.urlCount), end='')
