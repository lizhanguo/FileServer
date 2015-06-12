__author__ = 'ethan_huang'
import mysql.connector
import time
import os,hashlib

class SqlDB(object):
    def __init__(self):
        self.ServerPath = '/opt/rh'
    def OpenDB(self):
        try:
            conn = mysql.connector.connect(host='127.0.0.1',user='root',password='password',db ='file')
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE  user  (ID integer PRIMARY KEY AUTO_INCREMENT,
                                  NAME VARCHAR(20) NOT NULL ,
                                  PASSWORD  VARCHAR(50) NOT NULL ,
                                  STATUS  VARCHAR(10)  DEFAULT 'OK',
                                  DEPOSIT INT DEFAULT 1073741824,
                                  BALANCE INT DEFAULT 1073741824);''')

            cursor.execute('''CREATE TABLE  log  (TIME TIMESTAMP NOT NULL ,
                                  ID integer ,
                                  UID integer PRIMARY KEY AUTO_INCREMENT ,
                                  NAME TEXT NOT NULL,
                                  ACTION  TEXT NOT NULL,
                                  STATUS TEXT ,
                                  FOREIGN KEY (UID) REFERENCES user(ID) on DELETE CASCADE on UPDATE  CASCADE );''')
        except:
            print "Table already exists"
        return  conn
   # def OpenDB(self):
    #    conn = mysql.connector.connect(host='192.168.1.80',user='root',password='password',db ='file')
     #   return conn
    def Info(self):
        username = raw_input("Please input your name?\n")
        password = raw_input('please input your password?\n')
        password_md5 =  hashlib.new('md5',password).hexdigest()
        return  username,password_md5
    def AddUser(self):
        user = self.Info()
        conn = self.OpenDB()
        hel = conn.cursor()
        print user
        hel.execute('INSERT into user (NAME ,PASSWORD) VALUES  (%s,%s)',user )
        conn.commit()
        print "add users %s is successful" % user[0]
        os.chdir(self.ServerPath)
        os.mkdir(user[0])
        hel.close()
    def DelUser(self):
        delchoice = raw_input('Please enter the need to delete  user?')
        conn = self.OpenDB()
        hel = conn.cursor()
        hel.execute("DELETE from user WHERE name = '%s'" % delchoice)
        conn.commit()
        hel.close()

if __name__ == '__main__':
    a = SqlDB()
    print "admin console | add | del  |"
    while True:
        user = raw_input('>')
        if user == 'add':
            a.AddUser()
        elif user == 'del':
            a.DelUser()
        elif user == 'exit':
            print "bye bye"
            break

