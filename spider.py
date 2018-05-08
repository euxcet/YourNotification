#-*- coding: UTF-8 -*-
import requests, os, sys, cookielib, urllib, urllib2, re
from PIL import Image
from bs4 import BeautifulSoup
class Spider(object):
    def __init__(self):
        agent = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Mobile Safari/537.36'
        self.headers = {
            'User-Agent': agent
        }
        self.session = requests.session()
        self.session.headers = self.headers
        self.session.cookies = cookielib.LWPCookieJar()
        self.rootPath = 'http://learn.tsinghua.edu.cn'
        self.lesson = []
        f = open(r'D:\Course\Lessons\learn\ban.ini','r')
        self.ban = []
        for line in f:
            self.ban.append(re.compile(line[0:len(line)-1]))


    def clear(self,s):
        res = ''
        for i in xrange(0,len(s)):
            if (ord(s[i])>32 and ord(s[i]) != 160 and s[i]!='/'):
                res = res + s[i]
        return res
    def getName(self, url):
        session = self.session
        r = session.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        for link in soup.find_all('td', attrs = {'class': 'info_title'}):
            return self.clear(link.text)
    def getLesson(self, url, folderName):
        session = self.session
        r = session.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        files = []
        for link in soup.find_all('tr', attrs = {'class': 'tr1'}):
            files.append((link.find_all('td')[1].a['href'],self.clear(link.find_all('td')[1].a.text)))
        for link in soup.find_all('tr', attrs = {'class': 'tr2'}):
            files.append((link.find_all('td')[1].a['href'],self.clear(link.find_all('td')[1].a.text)))
        tot = 0
        for f in files:
            rh = session.head(self.rootPath + f[0])
            s =  rh.headers['Content-Disposition']
            point = 0
            for i in xrange(len(s)-1,0,-1):
                if (s[i]=='.'):
                    point = i
                    break
            isBan = 0
            for i in xrange(0, len(self.ban)):
                if (self.ban[i].match(s)):
                    isBan = 1
                    break
            if (isBan or (os.path.isfile(folderName + f[1].encode('utf-8')+'.'+s[point+1:len(s)-1]))):
                if (isBan):
                    print 'BAN ' + s
                continue

            r = session.get(self.rootPath + f[0])

            
            if ((not isBan) and (not os.path.isfile(folderName + f[1].encode('utf-8')+'.'+s[point+1:len(s)-1]))):
                print 'New file downloaded: '+folderName + f[1].encode('utf-8')+'.'+s[point+1:len(s)-1]
                with open((folderName + f[1].encode('utf-8')+'.'+s[point+1:len(s)-1]).replace('?',''), 'wb') as code:
                    for chunk in r.iter_content(chunk_size = 1024):
                        code.write(chunk)




    def login(self):
        lesson = self.lesson
        session = self.session
        logindata = {
            'userid': 'liu-yt16',
            'userpass': 'LYTlogic19981225',
            'submit1': '登录'
        }
        r = session.post('https://learn.tsinghua.edu.cn/MultiLanguage/lesson/teacher/loginteacher.jsp', data=logindata)
        r = session.get('http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/MyCourse.jsp?language=cn')
        soup = BeautifulSoup(r.text, 'html.parser')
        for link in soup.find_all('tr', attrs={'class': 'info_tr'}):
            lesson.append(self.rootPath+link.a['href'])
        for link in soup.find_all('tr', attrs={'class': 'info_tr2'}):
            lesson.append(self.rootPath+link.a['href'])
        #ban lesson
        banpath=[u'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/course_locate.jsp?course_id=148992',u'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/course_locate.jsp?course_id=148990',u'http://learn.tsinghua.edu.cnhttp://learn.cic.tsinghua.edu.cn/f/student/coursehome/2017-2018-1-00670143-90',u'http://learn.tsinghua.edu.cnhttp://learn.cic.tsinghua.edu.cn/f/student/coursehome/2017-2018-1-00640272-93']
        Path ='D:\\Course\\Lessons\\2017Fall\\'
        print lesson
        for i in banpath:
            if i in lesson:
                lesson.remove(i)
                print lesson
        for i in xrange(0, len(lesson)):
            lesson[i] =  lesson[i][0:43]+'lesson/student/download.jsp?'+lesson[i][len(lesson[i])-16:len(lesson[i])]
            if not os.path.exists(Path+self.getName(lesson[i])):
                os.mkdir(Path+self.getName(lesson[i]))
            if not os.path.exists(Path+self.getName(lesson[i])+'/files'):
                os.mkdir(Path+self.getName(lesson[i])+'/files')
            self.getLesson(lesson[i],Path+self.getName(lesson[i])+'/files/')
