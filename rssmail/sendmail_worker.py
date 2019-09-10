#! /usr/bin/env python
# -*- coding:utf-8 -*-

from .celery import app_rssmail
import json
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr


# 发送邮件主程序 ##
# smtp_server: 邮件服务器地址
# smtp_user: 邮件服务器登录账号
# mail_from: 发送人的email地址
# smtp_pass: 发送邮件服务器密码
# mail_to: 收件人邮件地址
# mail_msg: 邮件内容
# smtp_port: 邮件服务器端口，默认25
# send_dely: 邮件发送延时
# mail_title: 邮件主题
# mail_message: 邮件正文
# alias: 发件人别名

@app_rssmail.task(bind=True, queue='q_sendmail')
def sendmail(self, data):
    d = json.loads(data)

    mail_msg = gen_mailmessage(d['alias'], d['mail_from'], d['mail_to'], d['mail_title'], d['mail_message'])

    time.sleep(d['send_dely'])
    try:
        print("connect to smtp server {}".format(d['smtp_server']))
        if not d['smtp_port']:
            d['smtp_port'] = 25
        # print d['smtp_port']
        if int(d['smtp_port']) == 465 or int(d['smtp_port']) == 587:
            # print '1111'
            # sys.exit()
            # smtp = smtplib.SMTP_SSL('%s' % (d['smtp_server']), d['smtp_port'])
            smtp = smtplib.SMTP('%s' % (d['smtp_server']), d['smtp_port'])
            smtp.starttls()
        else:
            # print '2222'
            # sys.exit()
            smtp = smtplib.SMTP('%s' % (d['smtp_server']), d['smtp_port'])
        smtp.set_debuglevel(0)
        if d['smtp_user'] or d['smtp_pass']:
            smtp.login(d['smtp_user'], d['smtp_pass'])
        print("start to send email to {}".format(d['mail_to']))
        smtp.sendmail(d['mail_from'], d['mail_to'], mail_msg.as_string())
        smtp.close()
        print("From {} send to {} success\n".format(d['mail_from'], d['mail_to']))
    # except smtplib.SMTPResponseException, e:
    #     errcode = getattr(e, 'smtp_code', -1)
    #     errmsg = getattr(e, 'smtp_error', 'ignore')
    #     logs(0, "%d, %s" % (errcode, errmsg))
    #     logs(3, "%s to %s faild" % (from_email, d['mail_to']))
    # except smtplib.SMTPSenderRefused, e:
    #     errcode = getattr(e, 'smtp_code', -1)
    #     errmsg = getattr(e, 'smtp_error', 'ignore')
    #     sender = getattr(e, 'sender', 'None')
    #     logs(0, "%d, %s, %s" % (errcode, errmsg, sender))
    #     logs(3, "%s to %s faild" % (from_email, d['mail_to']))
    # except smtplib.SMTPRecipientsRefused, e:
    #     recipients = getattr(e, "recipients", "None")
    #     logs(0, "%s was refused" % recipients)
    #     logs(3, "%s to %s faild" % (from_email, d['mail_to']))
    except Exception as e:
        # if hasattr(e, 'd['mail_msg']'):
        #     logs(0, e.d['mail_msg'])
        # else:
        #     logs(0, e)
        print(e)
        print("from {} send to {} faild".format(d['mail_from'], d['mail_to']))


# 生成邮件内容
def gen_mailmessage(alias, mail_from, mail_to, mail_title, mail_message):
    # 拼接sendmail用的message，包含header和content
    msg = MIMEMultipart()
    if alias:
        msg['From'] = formataddr(
            (Header(alias, 'utf-8').encode(), mail_from))
    else:
        msg['From'] = mail_from

    msg['To'] = mail_to
    msg['Subject'] = Header(mail_title, charset='UTF-8')

    # 添加邮件内容
    # txt = MIMEText(mail_message, _subtype='plain', _charset='UTF-8')
    # 添加html的邮件内容
    # txt = MIMEText(mail_message, _subtype='html', _charset='UTF-8')
    mail_message_lower = mail_message.lower()
    if mail_message_lower.find('<html')==-1 and mail_message_lower.find('<p')==-1 and mail_message_lower.find('<br')==-1:
        mail_message = mail_message.replace('\n','<br>\n')
    txt = MIMEText(mail_message, _subtype='html', _charset='UTF-8')
    msg.attach(txt)

    return msg
