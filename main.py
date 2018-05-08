#coding=UTF-8
import json, requests, cookielib, re, time, getpass
from myemail import sendmail
from bs4 import BeautifulSoup


class Spider(object):
    def __init__(self, mu, mp, iu, ip):
        agent = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Mobile Safari/537.36'
        self.headers = {
            'User-Agent': agent
        }
        self.session = requests.session()
        self.session.headers = self.headers
        self.session.cookies = cookielib.LWPCookieJar()
        self.rootPath = 'http://learn.tsinghua.edu.cn'
        self.message = ''
        self.changedCourses = []
        self.courseNoteUrl = '/MultiLanguage/public/bbs/getnoteid_student.jsp?course_id='
        self.courseFileUrl = '/MultiLanguage/lesson/student/download.jsp?course_id='
        self.courseHwkUrl = '/MultiLanguage/lesson/student/hom_wk_brw.jsp?course_id='
        self.checklist = []
        self.mailUsername = mu
        self.mailPassword = mp
        self.infoUsername = iu
        self.infoPassword = ip
        with open('info.txt', 'r') as f:
            self.checklist = json.loads(f.read())

    def getNews(self, id):
        msg = []
        r = self.session.get(self.rootPath + self.courseNoteUrl + id)
        soup = BeautifulSoup(r.text, 'html.parser')
        for courseNote in soup.find_all('tr', class_=['tr1', 'tr2']):
            p = courseNote.find_all('td')
            if p[4].get_text() == u'未读' and id + p[1].get_text().strip() not in self.checklist:
                msg.append(p[1].get_text().strip())
                self.checklist.append(id + p[1].get_text().strip())

        return msg

    def getNewFiles(self, id):
        msg = []
        r = self.session.get(self.rootPath + self.courseFileUrl + id)
        soup = BeautifulSoup(r.text, 'html.parser')
        for courseFile in soup.find_all('tr', class_=['tr1', 'tr2']):
            p = courseFile.find_all('td')
            if p[5].get_text().strip() == u'新文件' and id + p[1].get_text().strip() not in self.checklist:
                msg.append(p[1].get_text().strip())
                self.checklist.append(id + p[1].get_text().strip())

        return msg

    def getNewHwk(self, id):
        msg = []
        r = self.session.get(self.rootPath + self.courseHwkUrl + id)
        soup = BeautifulSoup(r.text, 'html.parser')
        for courseFile in soup.find_all('tr', class_=['tr1', 'tr2']):
            p = courseFile.find_all('td')
            if p[3].get_text().strip() == u'尚未提交' and id + p[1].get_text().strip() not in self.checklist:
                msg.append(p[1].get_text().strip())
                self.checklist.append(id + p[1].get_text().strip())

        return msg

    def sendMessage(self):
        print 'Update'
        sendmail(self.mailUsername, self.mailPassword, self.mailUsername, u'通知', self.message)


    def work(self):
        session = self.session
        logindata = {
            'userid': self.infoUsername,
            'userpass': self.infoPassword,
            'submit1': '登录'
        }
        r = session.post('https://learn.tsinghua.edu.cn/MultiLanguage/lesson/teacher/loginteacher.jsp', data=logindata)
        r = session.get('http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/MyCourse.jsp?language=cn')

        soup = BeautifulSoup(r.text, 'html.parser')

        message = ''
        for link in soup.find_all('tr', class_=['info_tr', 'info_tr2']):

            courseInfo = link.find_all('td', attrs={'width': '55%'})[0]
            courseName = courseInfo.get_text().strip()
            courseUrl = courseInfo.a.get('href')
            courseId = re.search(r'\d+', courseUrl).group()
            courseNews = self.getNews(courseId)
            courseNewFiles = self.getNewFiles(courseId)
            courseNewHwk = self.getNewHwk(courseId)

            if courseNews or courseNewFiles or courseNewHwk:
                message += courseName + '\n'
                if courseNews:
                    message += u'新公告\n    ' + '\n    '.join(courseNews) + '\n'
                if courseNewFiles:
                    message += u'新文件\n    ' + '\n    '.join(courseNewFiles) + '\n'
                if courseNewHwk:
                    message += u'新作业\n    ' + '\n    '.join(courseNewHwk) + '\n'
                message += '\n'

        if message:
            self.message = message
            self.sendMessage()
            self.update()

        print 'Checked at ' +  time.asctime( time.localtime(time.time()))


    def update(self):
        with open('info.txt','w') as f:
            f.write(json.dumps(self.checklist))


if __name__=='__main__':

    mu=raw_input('Your QQ-email Address:')
    mp=getpass.getpass('Your QQ Password:')

    iu=raw_input('Your Tsinghua ID:')
    ip=getpass.getpass('Your Tsinghua Password:')
    

    sp=Spider(mu,mp,iu,ip)
    while(True):
        try:
            sp.work()

        except:
            pass

        time.sleep(1800)




