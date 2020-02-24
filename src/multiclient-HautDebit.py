import socket as s
import sys
import os
from _thread import *
import threading as t
import time as ti
class TestServer:
    def __init__(self):

        self.new_port = 0
        self.buffer = list()


        self.hostname = "0.0.0.0"

        self.clientip = ""

        self.sock=None

        self.port = int(sys.argv[1])

        self.server()

    def readFile(self, nomFich,buffer):
        try:

            f = open(nomFich.replace('\0','').strip(), "rb")
            num_seq = 0
            while 1:
                num_seq = num_seq + 1
                seq = bytes(str(num_seq).zfill(6).encode('utf8'))

                byte_s = f.read(1400)
                if not byte_s:
                    break
                result = seq + byte_s
                buffer.append(result)
                result = bytes()
        except FileNotFoundError:

            f = open(nomFich.replace('\0','').strip(), "wb")
        return  buffer


    def sendmsg(self, socket, buffer, clientip, j):
        socket.sendto(buffer[j], clientip)
        return

    def receive_ack(self, socket, buffe_trasmis, buffer_acked, cwnd,time):
        res = -3

        socket.settimeout(0.003+time)

        try:
            data, _ = socket.recvfrom(256)
            if str(data).find('ACK'):
                num = int(data.decode("utf-8")[3:9])

                if num == 0:
                    return num
                if num <= len(buffe_trasmis) and num >= list(buffer_acked.keys())[-1]:
                    if num in list(buffer_acked.keys()):
                        buffer_acked.update({num: buffer_acked.get(num) + 1})
                        buffe_trasmis[num - 1] = 1
                    else:
                        buffer_acked.update({num: 1})
                        buffe_trasmis[num - 1] = 1
                        for i in range(0, num - 1):
                            if buffe_trasmis[i] == 0:
                                buffe_trasmis[i] = 1
                        if num >= len(buffe_trasmis) - cwnd and cwnd > 0:
                            res = -2
                        else:
                            res = num
                            return res
                    if buffer_acked.get(num) >= 3:
                        res = num
                        return res

            else:
                res = -1

        except s.timeout:
            res = -1

            return res

        return res

    def communication(self,new_port,clientip):
        new_sock = s.socket(s.AF_INET, s.SOCK_DGRAM)
        new_sock.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
        new_sock.bind(('0.0.0.0', new_port))
        data, _ = new_sock.recvfrom(1400)
        start=ti.time()
        buffer=list()
        buffer=self.readFile(str(data.decode('utf-8')),buffer)
        buffer_tranmis = list()
        buffer_acked = dict()

        while 1:
            self.sendmsg(new_sock, buffer, clientip, 0)

            if self.receive_ack(new_sock, buffer_tranmis, buffer_acked, 0, 1) == -3:
                buffer_tranmis.append(1)
                buffer_acked.update({1: 1})

                break
        while 1:

            j = 1
            n = 12
            cwnd = 12

            resend = 0
            wait = 0

            while j < len(buffer):
                c = 0

                try:

                    while c < cwnd:
                        self.sendmsg(new_sock, buffer, clientip, j)
                        buffer_tranmis.append(0)
                        c += 1
                        j += 1
                    iter = 0
                    dup_acked = 0
                    time = 0
                    res = 0

                    while iter < cwnd + resend:

                        res = self.receive_ack(new_sock, buffer_tranmis, buffer_acked, cwnd, wait)
                        if res > 0:
                            if res != dup_acked:
                                self.sendmsg(new_sock, buffer, clientip, res)
                                dup_acked = res
                                n = 5
                            resend = 1

                        elif res == -2:

                            n = 12
                            resend = 0
                        elif res == -1:

                            resend = 0
                            time = time + 1
                            if iter == cwnd - 1:
                                break

                        buffer_acked.update({dup_acked: 0})
                        iter = iter + 1
                    if time >= cwnd - 1:
                        n = 3
                        resend = 0
                        j = list(buffer_acked.keys())[-1]

                    if time == 0:
                        wait = 0
                    else:
                        wait = 0.003/time

                    cwnd = n

                except IndexError:

                    break
            res = 0

            while 1:
                res = self.receive_ack(new_sock, buffer_tranmis, buffer_acked, cwnd, 0.001)
                if res == -1:
                    break
            num_no_acked = list(buffer_acked.keys())[-1]

            if num_no_acked < len(buffer_tranmis) and num_no_acked < len(buffer):
                res = 0
                while 1:
                    if list(buffer_acked.keys())[-1] >= len(buffer):
                        break
                    if res != -3:
                        self.sendmsg(new_sock, buffer, clientip, num_no_acked)
                    res = self.receive_ack(new_sock, buffer_tranmis, buffer_acked, 1, 0.001)
                    if res > 0 and res > num_no_acked:
                        num_no_acked = res
                    elif res == -2:
                        break

            msg = "FIN"
            new_sock.sendto(bytes(msg, 'utf8'),clientip)
            new_sock.close()

            self.buffer.clear()
            buffer_acked.clear()
            buffer_tranmis.clear()

            break

        return

    def server(self):
        self.sock = s.socket(s.AF_INET, s.SOCK_DGRAM)
        self.sock.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
        self.sock.bind((self.hostname, self.port))
        self.sock.settimeout(90)
        c=0

        while 1:
           try:
            data, addr = self.sock.recvfrom(256)
            if str(data.decode('utf-8'))[0:3]=="SYN":
                c+=1
                new_port=0
                new_port = self.port + c
                clientip = addr
                start_new_thread(self.communication, (new_port,clientip,))

                msg = "SYN-ACK" + str(new_port)
                self.sock.sendto(bytearray(msg, "utf8"), clientip)






            elif str(data.decode('utf-8'))[0:3]=="ACK":
                continue
            else:
                self.sock.close()
           except s.timeout:
                self.sock.close()
                break




if __name__ == '__main__':
    test1 = TestServer()
