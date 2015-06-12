__author__ = 'ethan_huang'
# -*-coding:utf-8 -*-
import SocketServer
import time
import hashlib
import mysql.connector
import pickle
import commands
import os
class fileserver(SocketServer.BaseRequestHandler):
    def OpenDB(self):
        conn = mysql.connector.connect(host='127.0.0.1',user='root',password='password',db ='file')
        return conn
    def Info(self):
        username = raw_input("Please input your name?\n")
        password = raw_input('please input your password?\n')
        password_md5 =  hashlib.new('md5',password).hexdigest()
        return  username,password_md5

    def login(self,username,password):
        print username,password
        conn = self.OpenDB()
        hel = conn.cursor()
        hel.execute("SELECT name,password from user where name = '%s'" % username)
        u = hel.fetchone()
        print u
        try:
            if username ==  u[0]:
                if password == u[1]:
                    hel.execute('INSERT into log (name,action,status) VALUES  (%s,%s,%s)',(username,'Login','OK') )
                    conn.commit()
                    return 'ok'
                else:
                    return 'error'
        except TypeError:
            return 'error'
    def File_Md5(self,filename):
        md = hashlib.md5()
        with open(filename,'rb') as f:
            while True:
                blk = f.read(4096)
                if not blk:break
                md.update(blk)
        return  md.hexdigest()
    def RXFile(self, filename):
        print "Start receive file!"
        f = open(filename, 'wb')
        self.request.send('ready')
        while True:
            data = self.request.recv(4096)
            if data == 'EOF':
                break
            f.write(data)
        f.close()
        Local_md5 =  self.File_Md5(filename)
        Client_md5 =  self.request.recv(1024)
        if Local_md5 == Client_md5:
            print "Receive file successful"
            return  1
        else:
            os.system('rm -fr %s' %filename)
            self.request.send('uploaderror')
            return 2

    def DXFile(self, filename):
        if os.path.exists(filename):
            file_size = os.stat(filename).st_size
            self.request.send(str(file_size))
            print "Start send file!"
            time.sleep(1)
            f = open(filename, 'rb')
            while True:
                data = f.read(4096)
                if not data:
                    break
                self.request.sendall(data)
            f.close()
            time.sleep(1)
            self.request.send('EOF')
            Local_md5 = self.File_Md5(filename)
            Client_md5 = self.request.recv(1024)
            print Local_md5
            print Client_md5
            if Local_md5 == Client_md5:
                print "Send file successful!"
                self.request.send('md5ok')
                return 1
            else:
                self.request.send('DownloadError')
                return 2
        else:
            self.request.send('NotFound')
            self.request.send('ready')

    def ListDir(self):
        result = commands.getoutput('ls -l')
        self.request.send(result)

    def DelFile(self,filename):
        os.system('rm -fr %s' %filename)

    def handle(self):
        ServerPath = '/opt/rh'
        print "get connection from :",self.client_address
        user = pickle.loads(self.request.recv(1024))
        if self.login(user[0],user[1]) == 'ok':
            os.chdir(ServerPath + '/'+user[0])
            self.request.send('ready')
            conn = self.OpenDB()
            hel = conn.cursor()
            while True:
                try:
                    data = self.request.recv(4096)
                    print "get data:", data
                    if not data:
                        print "break the connection!"
                        break
                    else:
                        if  data == "put":
                            filedata = self.request.recv(4096)
                            filedata = filedata.split('|')
                            filename = filedata[0]
                            filesize = int(filedata[1])
                            hel.execute("SELECT  deposit from user  WHERE name = '%s'" %user[0])
                            deposit = hel.fetchone()
                            new_deposit = deposit[0] - filesize
                            if new_deposit < filesize:
                                hel.execute('INSERT into log (name,action,status) '
                                            'VALUES  (%s,%s,%s)',(user[0],'upload','Fail') )
                                conn.commit()
                                self.request.send('Notspace')
                            else:
                                if self.RXFile(filename) == 1:
                                    hel.execute('INSERT into log (name,action,status) '
                                                'VALUES  (%s,%s,%s)',(user[0],'upload','OK') )
                                    hel.execute("update user SET deposit ='%s' WHERE name = '%s'" %(new_deposit,user[0]))
                                    conn.commit()
                                else:
                                    hel.execute('INSERT into log (name,action,status) '
                                                'VALUES  (%s,%s,%s)',(user[0],'upload','Fail') )
                                    conn.commit()
                        elif data == 'get':
                            filename=self.request.recv(4096)
                            print filename
                            if os.path.exists(filename):
                                if self.DXFile(filename) == 1:

                                    hel.execute('INSERT into log (name,action,status) '
                                                'VALUES  (%s,%s,%s)',(user[0],'Download','OK') )
                                    conn.commit()
                                else:
                                    hel.execute('INSERT into log (name,action,status) '
                                                'VALUES  (%s,%s,%s)',(user[0],'Download','Fail') )
                                    conn.commit()
                            else:
                                self.request.send('NotFound')
                                continue
                        elif data == 'show':
                            hel.execute("SELECT  deposit from user  WHERE name = '%s'" %user[0])
                            deposit = hel.fetchone()
                            n = deposit[0] / 1048576
                            self.request.send(str(n))
                        elif data == 'list':
                            self.ListDir()

                        elif data == 'del':
                            filename = self.request.recv(1024)
                            if os.path.exists(filename):
                                file_size = os.stat(filename).st_size
                                hel.execute("SELECT  deposit from user  WHERE name = '%s'" %user[0])
                                deposit = hel.fetchone()
                                new_deposit = deposit[0] + file_size
                                print new_deposit
                                hel.execute("update user SET deposit ='%s' WHERE name = '%s'" %(new_deposit,user[0]))
                                hel.execute('INSERT into log (name,action,status) '
                                            'VALUES  (%s,%s,%s)',(user[0],'remove','OK') )
                                conn.commit()
                                self.DelFile(filename)
                                self.request.send('ok')

                            else:
                                self.request.send('NotFound')
                        else:
                            print "get error!"
                            continue
                except Exception,e:
                    print "get error at:",e
        else:
            print user,"login error"




if __name__ == "__main__":
    host = ''
    port = 6000
    s = SocketServer.ThreadingTCPServer((host,port), fileserver)

    s.serve_forever()

