__author__ = 'ethan_huang'
# -*-coding:utf-8 -*-
import socket,sys,time,hashlib,pickle,os
class ServerClient(object):
    def __init__(self):
        try:
            self.ip = raw_input("IP>")
            self.server= (self.ip,6000)
            self.s = socket.socket()
            self.s.connect(self.server)
            x = pickle.dumps(self.Info())
            self.s.sendall(x)
            d = self.s.recv(1024)
            if d =='ready':
                print  "Welcome to use powerful file transfer tool,enter 'help' view the help"
                self.Action()
            else:
                print "Login error"
                self.s.close()
        except Exception,e:
             print "The remote server no response !",e


    def file_md5(self,filename):
        md = hashlib.md5()
        with open(filename,'rb') as f:
            while True:
                blk = f.read(4096)
                if not blk:break
                md.update(blk)
        return  md.hexdigest()
    def Report(self,count,Blocksize,Totalsize):
        percent = int(count * Blocksize * 100 / Totalsize)
        sys.stdout.write("\r%d% %" %percent + 'complete')
        sys.stdout.flush()

    def RXFile(self,filename):
        print "Start receive files"
        file_size =  self.s.recv(1024)
        print file_size
        f = open(filename, 'wb')
        num  = 0
        while True:
            data = self.s.recv(4096)
            if data == 'EOF':
                break
            num +=1
            f.write(data)
            self.Report(num,4096,int(file_size))
        f.close()
        self.s.send(self.file_md5(filename))
        print "\nReceive file success!"

    def DXFile(self,filename,file_size):
        print "Start send files"
        print file_size
        f = open(filename, 'rb')
        num = 0
        while True:
            data = f.read(4096)
            if not data:
                break
            num +=1
            self.s.sendall(data)
            self.Report(num,4096,file_size)
        f.close()
        time.sleep(1)
        self.s.sendall('EOF')
        self.s.send(self.file_md5(filename))
        print "\nSend file successful!"

    def Info(self):
            username = raw_input("name>")
            password = raw_input('password>')
            password_md5 =  hashlib.new('md5',password).hexdigest()
            return  username,password_md5

    def Action(self):
        while True:
                action = raw_input(">>").strip()
                if not action:
                    continue
                if action == 'put':
                    file= raw_input('path:')
                    if os.path.exists(file):
                        self.s.send(action)
                        file_name = os.path.basename(file)
                        file_size = os.stat(file).st_size
                        self.s.send(file_name +'|'+ str(file_size))
                        message = self.s.recv(1024)
                        if  message == 'Notspace':
                            print 'Not enough disk space'
                            continue
                        else:
                            self.DXFile(file,file_size)
                            continue
                    else:
                        print 'Not found file'
                        continue
                elif action == 'get':
                    self.s.send(action)
                    file= raw_input('filename:')
                    self.s.send(file)
                    self.RXFile(file)
                    message = self.s.recv(4096)
                    if message == 'DownloadError':
                        os.remove(file)
                        print "Download error,file has been remove, Please download again"
                    else:
                        print  "Download  OK"
                elif action == 'list':
                    self.s.send(action)
                    print self.s.recv(4096)
                    continue
                elif action == 'del':
                    self.s.send(action)
                    file= raw_input('filename:')
                    self.s.send(file)
                    q = self.s.recv(1024)
                    if q == 'NotFound':
                        print "Not found file, Please try again"
                    elif  q == 'ok':
                        print "Delete %s successful" %file
                    continue
                elif action  == 'show':
                    self.s.send(action)
                    print "Available:         %sMB" %self.s.recv(4096)
                    continue
                elif action == 'exit':
                    print "Bye Bye"
                    self.s.close()
                    break
                elif action == 'help':
                    print """
        del    Remove
        list   View
        put    Upload
        get    Download
        show   See the available space"""
                else:
                    print "command error!"



if __name__ == '__main__':
    fileserver = ServerClient()
