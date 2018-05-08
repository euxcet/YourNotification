#coding=UTF-8
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr


def sendmail(sender, password, receiver, subject, message):
    try:
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['From'] = formataddr(['Logic', sender])
        msg['To'] = formataddr(['me', receiver])
        msg['Subject'] = subject

        server = smtplib.SMTP_SSL('smtp.qq.com', 465)
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()

    except:
        print 'ERROR'

