# GetStarsCode
批量下载github用户已star项目的源码

1. getUrl.py：爬取用户star项目的链接，将项目链接存本地ProjectUrl_stars.txt
2. mtp_getProject.py：请求ProjectUrl_stars.txt中的项目链接，爬取项目源码下载链接，多线程下载
