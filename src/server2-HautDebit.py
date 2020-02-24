import socket as s
import sys
import os
import time as t
import random as r
class TestServer:
    def __init__(self):

        self.new_port = 0
        self.buffer = list()


        self.hostname = "0.0.0.0"

        self.clientip = ""
        self.sock=None
        self.new_port=0
        self.port = int(sys.argv[1])

        self.server()

    def readFile(self, nomFich):
        try:
            f = open(nomFich.replace('\0','').strip(), "rb")
            num_seq = 0
            while 1:
                num_seq = num_seq + 1
                seq = bytes(str(num_seq).zfill(6).encode('utf8'))

                byte_s = f.read(1450)
                if not byte_s:
                    break
                result = seq + byte_s
                self.buffer.append(result)
                result = bytes()
        except FileNotFoundError:

            f = open(nomFich.strip(), "wb")

        return

    def handshake(self):
        self.sock = s.socket(s.AF_INET, s.SOCK_DGRAM)
        self.sock.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
        self.sock.bind((self.hostname, self.port))
        self.sock.settimeout(40)
        data, addr = self.sock.recvfrom(256)

        if str(data).find("SYN"):
            self.new_port = self.port + r.randint(1,100)
            self.clientip = addr
            msg = "SYN-ACK" + str(self.new_port)
            self.sock.sendto(bytearray(msg, "utf8"), self.clientip)




        else:

            self.sock.close()

        return

    def sendmsg(self, socket, buffer, clientip, j):
        socket.sendto(buffer[j], clientip)
        return

    def receive_ack(self, socket, buffe_trasmis, buffer_acked, cwnd,wait):
        res = -3
        socket.settimeout(0.02*wait)

        try:
            data, _ = socket.recvfrom(256)
            if str(data).find('ACK'):

                num = int(data.decode("utf-8")[3:9])

                if num == 0:
                    return num
                if num <= len(buffe_trasmis) and num >= list(buffer_acked.keys())[-1]:
                    if num in list(buffer_acked.keys()):
                        buffer_acked.update({num: buffer_acked.get(num) + 1})

                    else:
                        buffer_acked.update({num: 1})

                        if num ==len(buffe_trasmis) :
                            res = -2

                    if buffer_acked.get(num) > 2:
                        res = num
                        return res
            else:
                res = -1

        except s.timeout:
            res = -1

            return res
        return res

    def communication(self):
            self.new_sock = s.socket(s.AF_INET, s.SOCK_DGRAM)
            self.new_sock.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
            self.new_sock.bind(('0.0.0.0', self.new_port))
            data, _ = self.new_sock.recvfrom(256)
            start=t.time()
            self.readFile(str(data.decode('utf-8')))
            buffer_tranmis = list()
            buffer_acked = dict()


            while 1:
                self.sendmsg(self.new_sock, self.buffer, self.clientip, 0)
                #if self.receive_ack(self.new_sock, buffer_tranmis, buffer_acked, 0,1) == -3:
                buffer_tranmis.append(1)
                buffer_acked.update({1: 1})

                break
            while 1:

                j = 1
                n = 25
                cwnd = 25
                wait=1

                while j < len(self.buffer):
                    c = 0

                    try:
                        while c < cwnd:
                            self.sendmsg(self.new_sock, self.buffer, self.clientip, j)
                            buffer_tranmis.append(0)
                            c += 1
                            j += 1

                        iter = 0
                        dup_acked = 0
                        time = 0
                        res = 0
                        if cwnd == 3:
                            cwnd = cwnd + 1
                        while iter < cwnd:
                            res = self.receive_ack(self.new_sock, buffer_tranmis, buffer_acked, cwnd,wait)
                            if res > 0 and res != dup_acked:
                                self.sendmsg(self.new_sock, self.buffer, self.clientip, res)
                                n = 25
                                dup_acked = res
                            elif res == -2:
                                n = 25
                                break
                            elif res == -1:
                                time = time + 1
                                if iter == cwnd - 1:
                                    break
                            buffer_acked.update({dup_acked: 0})
                            iter = iter + 1

                        if time >= cwnd - 1:
                            n=1
                        if time==0:
                            wait=1
                        else:
                            wait=time



                        cwnd = n
                    except IndexError:
                        break
                res = 0

                while 1:
                    res = self.receive_ack(self.new_sock, buffer_tranmis, buffer_acked, cwnd,1)
                    if res == -1:
                        break
                num_no_acked = list(buffer_acked.keys())[-1]

                if num_no_acked < len(buffer_tranmis):
                    while 1:
                        if res != -3:
                            self.sendmsg(self.new_sock, self.buffer, self.clientip, num_no_acked)
                        res = self.receive_ack(self.new_sock, buffer_tranmis, buffer_acked, 1,1)
                        if res > 0:
                            num_no_acked = res
                        elif res == -2:
                            break
                msg = "FIN"
                self.new_sock.sendto(bytes(msg, 'utf8'), self.clientip)
                self.new_sock.close()
                #print((len(self.buffer)*1450/(t.time()-start))/10**6)
                self.buffer.clear()
                buffer_acked.clear()
                buffer_tranmis.clear()
                break

            return

    def server(self):

        while 1:
            try:
                self.handshake()
                self.communication()
            except s.timeout:
                #print("Connexion timeout ")
                self.sock.close()
                break
if __name__ == '__main__':
    test1 = TestServer()
