#! /usr/bin/env python
# -*- coding:utf-8 -*-

from .celery import app_rssemail
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
@app_rssemail.task(bind=True, queue='q_sendmail')
def sendmail(self,data):
    #d['mail_to'], message, d['mail_from'], port, d['smtp_server']='localhost', s_passwd=''):
    global g_log_folder

    d = json.load(data)

    time.sleep(d['send_dely'])
    try:
        printf("connect to smtp server %s" % d['smtp_server'])
        smtp = smtplib.SMTP()
        smtp.set_debuglevel(0)
        smtp.connect('%s' % (d['smtp_server']), port)
        #smtp.connect('smtp.%s'%(d['smtp_server']), 25)
        # smtp.helo()
        smtp.ehlo_or_helo_if_needed()
        if port == 465:
            smtp.starttls()
        if s_passwd:
            smtp.login(d['smtp_user'], d['smtp_pass'])
        printf("start to send email to %s" % d['mail_to'])
        smtp.sendmail(d['mail_from'], d['mail_to'], d['mail_msg'].as_string())
        smtp.close()
        printf("%s to %s success\n" % (d['mail_from'], d['mail_to']))
    except smtplib.SMTPResponseException as e:
        errcode = getattr(e, 'smtp_code', -1)
        errmsg = getattr(e, 'smtp_error', 'ignore')
        printf("%d, %s" % (errcode, errmsg))
        printf("%s to %s faild" % (d['mail_from'], d['mail_to']))
    except smtplib.SMTPSenderRefused as e:
        errcode = getattr(e, 'smtp_code', -1)
        errmsg = getattr(e, 'smtp_error', 'ignore')
        sender = getattr(e, 'sender', 'None')
        printf("%d, %s, %s" % (errcode, errmsg, sender))
        printf("%s to %s faild" % (d['mail_from'], d['mail_to']))
    except smtplib.SMTPRecipientsRefused as e:
        recipients = getattr(e, "recipients", "None")
        printf("%s was refused" % recipients)
        printf("%s to %s faild" % (d['mail_from'], d['mail_to']))
    except Exception as e:
        if hasattr(e, 'message'):
            printf(e.message)
        else:
            printf(e)

        printf("%s to %s faild" % (d['mail_from'], d['mail_to']))