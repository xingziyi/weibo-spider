import redis
#import socket
import threading
#s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.bind(('127.0.0.1', 9999))
#s.listen(1)
#conn,addr = s.accept()
#number = 0
#print(addr)
#ip = input("ip:")
#port = int(input("port:"))
#redis_connection = redis.Redis(host='127.0.0.1', port=6379, db=0)

# while True:
#     if (number < redis_connection.dbsize()):
#         data = redis_connection.get(number)
#         number = number + 1
#         print(data)
#         s.sendto(data, (ip, port))
#s.close()
# import threading
# address='127.0.0.1'
# port=1124
# buffsize=1024
# s = socket(AF_INET, SOCK_STREAM)
# s.bind((address,port))
# s.listen(1)     #最大连接数

# def tcplink(sock,addr):
#     while True:
#         recvdata=clientsock.recv(buffsize).decode('utf-8')
#         if recvdata=='exit' or not recvdata:
#             break
#         senddata=recvdata+'from sever'
#         clientsock.send(senddata.encode())
#     clientsock.close()

# while True:
#     clientsock,clientaddress=s.accept()
#     print('connect from:',clientaddress)
# #传输数据都利用clientsock，和s无关
#     t=threading.Thread(target=tcplink,args=(clientsock,clientaddress))  #t为新创建的线程
#     t.start()
# s.close()

from socket import *
#import threading
address = '0.0.0.0'
port = 11240
buffsize = 1024
s = socket(AF_INET, SOCK_STREAM)
s.bind((address, port))
print("waiting for client")
s.listen(1)  #最大连接数
clientsock, clientaddress = s.accept()
print('connect from:', clientsock, clientaddress)
redis_connection = redis.Redis(host='127.0.0.1', port=6379, db=0)
number = 1
while True:
    dbnum = redis_connection.dbsize()
    recvdata = clientsock.recv(buffsize).decode('utf-8')
    need = int(recvdata)
    if (need == 0):
        continue
    if recvdata == 'exit':
        break
    if (number + need <= dbnum):
        i = number
        while i < number + need:
            senddata = redis_connection.get(i)
            senddata = str(senddata, encoding = "utf8")
            senddata = senddata + ' '
            senddata = bytes(senddata, encoding = "utf8")
            #senddata = str(senddata)
            clientsock.send(senddata)#.encode())
            #clientsock.push(senddata)
            i = i + 1
        number = number + need
    else:
        i = number
        size = dbnum;
        while i < dbnum:
            senddata = redis_connection.get(i)
            clientsock.send(senddata)#.encode())
            i = i + 1
        number = dbnum
clientsock.close()
s.close()