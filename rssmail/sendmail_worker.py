#! /usr/bin/env python
# -*- coding:utf-8 -*-

from .celery import app_rssmail
import json
import smtplib
import time


## 发送邮件主程序 ##
# smtp_server: 邮件服务器地址
# smtp_user: 邮件服务器登录账号
# mail_from: 发送人的email地址
# smtp_pass: 发送邮件服务器密码
# mail_to: 收件人邮件地址
# mail_msg: 邮件内容
# smtp_port: 邮件服务器端口，默认25
# send_dely: 邮件发送延时
@app_rssmail.task(bind=True, queue='q_sendmail')
def sendmail(self,data):
    #d['mail_to'], d['mail_msg'], d['mail_from'], port, d['smtp_server']='localhost', d['smtp_pass']=''):
    global g_log_folder

    d = json.load(data)

    time.sleep(d['send_dely'])
    try:
        printf("connect to smtp server %s" % d['smtp_server'])
        if not d['smtp_port']:
            d['smtp_port'] = 25
        #print d['smtp_port']
        if int(d['smtp_port']) == 465 or int(d['smtp_port']) == 587:
            #print '1111'
            #sys.exit()
            # smtp = smtplib.SMTP_SSL('%s' % (d['smtp_server']), d['smtp_port'])
            smtp = smtplib.SMTP('%s' % (d['smtp_server']), d['smtp_port'])
            smtp.starttls()
        else:
            #print '2222'
            #sys.exit()
            smtp = smtplib.SMTP('%s' % (d['smtp_server']), d['smtp_port'])
        smtp.set_debuglevel(0)
        if d['smtp_user'] or d['smtp_pass']:
            smtp.login(d['smtp_user'], d['smtp_pass'])
        printf("start to send email to %s" % d['mail_to'])
        smtp.sendmail(d['mail_from'], d['mail_to'], d['mail_msg'].as_string())
        smtp.close()
        printf("%s to %s success\n" % (from_email, d['mail_to']))
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
        printf("%s to %s faild" % (from_email, d['mail_to']))