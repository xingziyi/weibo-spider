from bs4 import BeautifulSoup
import re
import time
from urllib import request
import queue
import socket
hostip = "192.168.43.71"
hostport = 11240
sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sk.connect((hostip,hostport))
urlq = queue.Queue(200)
sk.sendall('200'.encode())
while 1:
    stime = 150/urlq.qsize()
    time.sleep(stime)
    print("qurl_size:"+str(urlq.qsize()))
    if urlq.qsize()<= 50:
        accept_date = str(sk.recv(1025),"utf8").split()
        nu = 200- urlq.qsize()
        sk.sendall(str(nu).encode())
        for i in accept_date:
            urlq.put(i)
    if urlq.qsize() != 0:
        url = urlq.get() 
        url ="https://weibo.com/u/"+url
        print(url)
        headers = {  
    "Accpet":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Connection":"keep-alive",
    "Cookie":"SINAGLOBAL=1010773572493.4042.1521630820528; UM_distinctid=16306c1a3b7ae5-0b9939f11ce32a-3b72025b-1fa400-16306c1a3b835b; UOR=blog.sina.com.cn,service.weibo.com,www.baidu.com; un=xingziyi@aliyun.com; SUB=_2AkMtshscf8NxqwJRmP4Qzm7gbYtyywDEieKb7urHJRMxHRl-yT9jqk8_tRB6BjI18zKLwlc7VNv3HKdvSA52igGxBzO7; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WFaUzQQWJ1juubA54DNhORd; _T_WM=5c48732acb4c01b69e51414218c42abe; YF-Page-G0=f017d20b1081f0a1606831bba19e407b; _s_tentry=-; Apache=6492754373532.361.1525825198913; ULV=1525825198920:10:7:5:6492754373532.361.1525825198913:1525789953934",
    "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36",
    "Host":'weibo.com'  
}  
        req = request.Request(url=url,data=None,headers=headers,method="GET")
        res = request.urlopen(req)
        soup = BeautifulSoup(res,"html.parser")
        s = soup.get_text()
        username =re.findall(r'<h1 class=\\"username\\">(.+?)<\\/h1>',s)
        if len(username) = 0:
            continue
        print(username)
        fb = re.findall(r'<strong class=\\".+?\\">(.+?)<\\/strong>',s)
        fan = fb[1]
        wb_num = fb[2]
        grade = re.findall(r'<span>Lv.(.+?)<\\/span>',s)
        print(grade)
        sex = re.findall(r'<i class=\\"W_icon icon_pf_(.+?)\\">',s)
        print(sex)
        intro = re.findall(r'<div class=\\"pf_intro\\" title=\\"(.+?)\\">',s)
        print(intro)
        text = re.findall(r'<div class=\\"WB_text .+?\\" node-type=\\"feed_list_content\\" nick-name=\\".+?\\">\\n(.+?)<\\/div>',s)
        print(len(text))
