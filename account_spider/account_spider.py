import queue
import time
import redis
import base64
import rsa
import binascii
import requests
import re
from PIL import Image
import random
from urllib.parse import quote_plus
#import http.cookiejar as cookielib
import urllib.request
from bloom_filter import BloomFilter

agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0'
headers = {'User-Agent': agent}

yipa = BloomFilter()
result = BloomFilter()
zhengpa = queue.Queue()


class WeiboLogin(object):
    def __init__(self, user, password):
        super(WeiboLogin, self).__init__()
        self.user = user
        self.password = password
        self.session = requests.Session()
        self.index_url = "http://weibo.com/login.php"
        self.session.get(self.index_url, headers=headers, timeout=2)
        self.postdata = dict()

    def get_su(self):
        username_quote = quote_plus(self.user)
        username_base64 = base64.b64encode(username_quote.encode("utf-8"))
        return username_base64.decode("utf-8")

    def get_server_data(self, su):
        pre_url = "http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su="
        pre_url = pre_url + su + "&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_="
        pre_url = pre_url + str(int(time.time() * 1000))
        pre_data_res = self.session.get(pre_url, headers=headers)
        # print(pre_data_res.text)
        sever_data = eval(
            pre_data_res.content.decode("utf-8").replace(
                "sinaSSOController.preloginCallBack", ''))
        return sever_data

    def get_password(self, servertime, nonce, pubkey):
        """对密码进行 RSA 的加密"""
        rsaPublickey = int(pubkey, 16)
        key = rsa.PublicKey(rsaPublickey, 65537)  # 创建公钥
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(
            self.password)  # 拼接明文js加密文件中得到
        message = message.encode("utf-8")
        passwd = rsa.encrypt(message, key)  # 加密
        passwd = binascii.b2a_hex(passwd)  # 将加密信息转换为16进制。
        return passwd

    def get_cha(self, pcid):
        cha_url = "https://login.sina.com.cn/cgi/pin.php?r="
        cha_url = cha_url + str(int(random.random() * 100000000)) + "&s=0&p="
        cha_url = cha_url + pcid
        cha_page = self.session.get(cha_url, headers=headers)
        with open("cha.jpg", 'wb') as f:
            f.write(cha_page.content)
            f.close()
        try:
            im = Image.open("cha.jpg")
            im.show()
            im.close()
        except Exception as e:
            print(u"reinput")

    def pre_login(self):
        su = self.get_su()  # su 是加密后的用户名
        sever_data = self.get_server_data(su)
        servertime = sever_data["servertime"]
        nonce = sever_data['nonce']
        rsakv = sever_data["rsakv"]
        pubkey = sever_data["pubkey"]
        showpin = sever_data["showpin"]
        password_secret = self.get_password(servertime, nonce, pubkey)
        self.postdata = {
            'entry':
            'weibo',
            'gateway':
            '1',
            'from':
            '',
            'savestate':
            '7',
            'useticket':
            '1',
            'pagerefer':
            "https://passport.weibo.com",
            'vsnf':
            '1',
            'su':
            su,
            'service':
            'miniblog',
            'servertime':
            servertime,
            'nonce':
            nonce,
            'pwencode':
            'rsa2',
            'rsakv':
            rsakv,
            'sp':
            password_secret,
            'sr':
            '1366*768',
            'encoding':
            'UTF-8',
            'prelt':
            '115',
            "cdult":
            "38",
            'url':
            'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype':
            'TEXT'
        }
        return sever_data

    def login(self):
        try:
            sever_data = self.pre_login()
            login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)&_'
            login_url = login_url + str(time.time() * 1000)
            login_page = self.session.post(
                login_url, data=self.postdata, headers=headers)
            ticket_js = login_page.json()
            ticket = ticket_js["ticket"]
        except Exception as e:
            sever_data = self.pre_login()
            login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)&_'
            login_url = login_url + str(time.time() * 1000)
            pcid = sever_data["pcid"]
            self.get_cha(pcid)
            self.postdata['door'] = input(u"请输入验证码\n")
            login_page = self.session.post(
                login_url, data=self.postdata, headers=headers)
            ticket_js = login_page.json()
            ticket = ticket_js["ticket"]
        save_pa = r'==-(\d+)-'
        ssosavestate = int(re.findall(save_pa, ticket)[0]) + 3600 * 7
        jump_ticket_params = {
            "callback": "sinaSSOController.callbackLoginStatus",
            "ticket": ticket,
            "ssosavestate": str(ssosavestate),
            "client": "ssologin.js(v1.4.19)",
            "_": str(time.time() * 1000),
        }
        jump_url = "https://passport.weibo.com/wbsso/login"
        jump_headers = {
            "Host": "passport.weibo.com",
            "Referer": "https://weibo.com/",
            "User-Agent": headers["User-Agent"]
        }
        jump_login = self.session.get(
            jump_url, params=jump_ticket_params, headers=jump_headers)
        uuid = jump_login.text
        uuid_pa = r'"uniqueid":"(.*?)"'
        uuid_res = re.findall(uuid_pa, uuid, re.S)[0]
        web_weibo_url = "http://weibo.com/%s/profile?topnav=1&wvr=6&is_all=1" % uuid_res
        weibo_page = self.session.get(web_weibo_url, headers=headers)
        weibo_pa = r'<title>(.*?)</title>'
        #print(weibo_page.content.decode("utf-8"))
        userID = re.findall(weibo_pa,
                            weibo_page.content.decode("utf-8", 'ignore'),
                            re.S)[0]
        print(u"账户 %s 登陆成功!" % userID)
        Mheaders = {"Host": "login.sina.com.cn", "User-Agent": agent}
        _rand = str(time.time())
        mParams = {
            "url": "https://m.weibo.cn/",
            "_rand": _rand,
            "gateway": "1",
            "service": "sinawap",
            "entry": "sinawap",
            "useticket": "1",
            "returntype": "META",
            "sudaref": "",
            "_client_version": "0.6.26",
        }
        murl = "https://login.sina.com.cn/sso/login.php"
        mhtml = self.session.get(murl, params=mParams, headers=Mheaders)
        mhtml.encoding = mhtml.apparent_encoding
        mpa = r'replace\((.*?)\);'
        
        mres = re.findall(mpa, mhtml.text)
        Mheaders["Host"] = "passport.weibo.cn"
        self.session.get(eval(mres[0]), headers=Mheaders)
        Mheaders["Host"] = "weibo.cn"
        zhengpa.put(2056394313)
        zhengpa.put(234535428)
        result.add(2056394313)
        result.add(234535428)
        redis_connection = redis.Redis(host='127.0.0.1', port=6379, db=0)
        serial_number = 0
        while True:
            if zhengpa.qsize() == 0:
                return
            pa = zhengpa.get()
            yipa.add(pa)
            #https://weibo.cn/2056394313/fans
            for i in range(1, 20):
                Set_url = "https://weibo.cn/" + str(pa) + "/fans?page=" + str(i)
                pro = self.session.get(Set_url, headers=Mheaders)
                ss = re.findall(r"<a href=\"http://weibo.cn/u/(.+?)\">",
                                pro.text)
                #print(ss)
                if len(ss) == 0:
                    break
                for j in ss:
                    if j not in result:
                        result.add(j)
                        #if (redis_connection.get(j) == None):
                        redis_connection.set(serial_number, j)
                        print(serial_number)
                        serial_number = serial_number + 1
                    #result.add(j)
                    if j in yipa:
                        continue
                    else:
                        zhengpa.put(j)
                    #print(result)
                time.sleep(random.randint(1, 8))
                #print(zhengpa.qsize())
                # print("result length:\n")
                # print(len(result))
                # print("result:\n")
                # print(result)

        # f = open('C:/Users/a1369/Desktop/data.txt', 'w')
        # f.writelines(
        #     '%s' % "http://weibo.cn/u/" + str(item) + "\n" for item in result)

        #print(result)
        #print(pro.text)

        # yipa = set()
        # result = set()
        # zhengpa = queue.Queue()

        #Set_url = "https://weibo.cn"
        # pro = self.session.get(Set_url, headers=Mheaders)
        # pa_login = r'isLogin":true,'
        # login_res = re.findall(pa_login, pro.text)
        #print(pro.text)
        # fhandle = open("C:/Users/a1369/Desktop/temp/1.html","wb")
        # fhandle.write(str.encode(pro.text))
        # fhandle.close()
        #self.session.cookies.save()


if __name__ == '__main__':
    username = "13480804423"  # 用户名
    password = "782190df"  # 密码
    weibo = WeiboLogin(username, password)
    weibo.login()
