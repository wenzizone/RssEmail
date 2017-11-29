#! /usr/bin/env python
# -*- coding:utf-8 -*-

import csv
import sys
import os
import smtplib
import base64
import time
import argparse
import logging
from jinja2 import Environment, FileSystemLoader


# global variables
g_varfile = ''
g_contentfile = ''
g_titefile = ''
g_delaytime = ''
g_frommail = ''
g_smtp = ''
g_passwd = ''
g_columns = ''
g_log_folder = os.path.join(os.path.split(
    os.path.realpath(sys.argv[0]))[0], 'log')


# 解析传进来的参数
def parse_args():
    global g_varfile, g_contentfile, g_titlefile, g_delaytime, g_log_folder, g_frommail, g_smtp, g_passwd, g_columns

    parser = argparse.ArgumentParser(description='邮件群发系统')
    parser.add_argument('--file', nargs='?', required=True, help='变量文件')
    parser.add_argument('--content', nargs='?', required=True, help='邮件内容文件')
    parser.add_argument('--title', nargs='?', required=True, help='邮件标题文件')
    parser.add_argument('-t', nargs='?', required=False, help='每封邮件间隔时间')
    parser.add_argument('--from', nargs='?', required=False, help='发件人邮件地址')
    parser.add_argument('--smtp', nargs='?', required=False, help='发件邮件服务器地址')
    parser.add_argument('--passwd', nargs='?',
                        required=False, help='发件邮件服务器登录密码')
    parser.add_argument('-c', nargs='?', required=False, help='变量所在列')
    parser.add_argument('--log', nargs='?', required=False,
                        help='日志存储位置,默认当前程序运行目录')

    args = vars(parser.parse_args())
    if args['file'] != None:
        g_varfile = args['file']
    if args['content'] != None:
        g_contentfile = args['content']
    if args['title'] != None:
        g_titlefile = args['title']
    if args['t'] != None:
        g_delaytime = args['t']
    if args['log'] != None:
        g_log_folder = args['log']
    if args['from'] != None:
        g_frommail = args['from']
    if args['smtp'] != None:
        g_smtp = args['smtp']
    if args['passwd'] != None:
        g_passwd = args['passwd']
    if args['c'] != None:
        g_columns = args['c']


# 读取变量文件，获取收件人地址和所有变量
def parse_var_file():
    global g_varfile, g_delaytime, g_columns

    columns_array = g_columns.split(',')

    with open(g_varfile) as fp:
        for line in fp:
            dic_vars = {}
            time.sleep(int(g_delaytime))  # 休眠间隔时间
            line_array = line.split(',')
            to_mail = line_array[0]
            # 设置变量对应的字段，用来替换模板文件中对应的变量位置
            for i in columns_array:
                dic_vars['var' + i] = line_array[int(i)]

            email_title = create_title(dic_vars)
            email_message = create_message(dic_vars)

            print "email_tile: %s" % email_title
            print "email_message: %s" % email_message

            # 准备发送邮件


# 从模板文件生成邮件主题
def create_title(vars):
    global g_titlefile

    THIS_DIR = os.path.dirname(g_titlefile)
    This_file = os.path.basename(g_titlefile)

    # Create the jinja2 environment.
    # Notice the use of trim_blocks, which greatly helps control whitespace.
    j2_env = Environment(loader=FileSystemLoader(THIS_DIR),
                         trim_blocks=True)
    return j2_env.get_template(This_file).render(vars)


# 从模板文件生成邮件内容
def create_message(vars):
    global g_contentfile

    THIS_DIR = os.path.dirname(g_contentfile)
    This_file = os.path.basename(g_contentfile)

    # Create the jinja2 environment.
    # Notice the use of trim_blocks, which greatly helps control whitespace.
    j2_env = Environment(loader=FileSystemLoader(THIS_DIR),
                         trim_blocks=True)
    return j2_env.get_template(This_file).render(vars)


## 发送邮件主程序 ##
# domain: 邮件服务器地址
# s_email: 发送人的email地址
# s_passwd: 发送邮件服务器密码
# r_email: 收件人邮件地址
# message: 邮件内容
# title: 邮件主题
# port: 邮件服务器端口，默认25
def sendmail(domain='localhost', s_email='root@localhost', s_passwd='', r_email, message, port=25):
    global g_log_folder

    try:
        smtp = smtplib.SMTP()
        smtp.set_debuglevel(0)
        smtp.connect('smtp.%s' % (domain), port)
        #smtp.connect('smtp.%s'%(domain), 25)
        # smtp.helo()
        smtp.starttls()
        smtp.login(s_email, s_passwd)
        smtp.sendmail(s_email, r_email, message)
        smtp.close()
        logfh.write("%s to %s success\n" % (s_email, r_email))
        # logfh.write("success\n")
        print "%s to %s success" % (s_email, r_email)
    except:
        logfh.write("%s to %s faild\n" % (s_email, r_email))
        # logfh.write("faild\n")
        print "%s to %s faild" % (s_email, r_email)
        pass

# main
time.sleep(delaytime)
if os.path.exists(logdir) == False:
    os.mkdir(logdir)
    # pass
logfile = os.path.basename(emailfile)
logfile = logfile.split('.')[0]
logfile = logdir + '/' + logfile + '.log'
print logfile
while True:

    fh = open(emailfile)
    csvfile = csv.reader(fh)
    logfh = open(logfile, 'w')
    logfh.write("==== " + str(datetime.datetime.today()) + " ====\n")
    logfh.close()
    logfh = open(logfile, 'a')

    for lines in csvfile:
        s_email = lines[0]
        s_passwd = lines[1]
        r_email = lines[2]
        r_passwd = lines[3]

        #mail_title = get_random_file_content(emailfile, 4, len(lines))
        (content, mail_title) = get_random_56_content(emailfile, len(lines))
        # print mail_title
        for i in range(6, len(lines)):
            content_tmp = get_random_file_content(emailfile, i, len(lines))
            content = content + content_tmp

        if s_email == '':
            continue
        tmp = s_email.split('@')
        if len(tmp) < 2:
            continue
        if tmp[1] == 'hotmail.com':
            domain = 'live.com'
            port = 587
        else:
            domain = tmp[1]
            port = 25

        # print s_email,",",domain,",",s_passwd,",",r_email
        # print mail_title,'---',content
        encode_content = base64.b64encode(content)
        '''
            content = """
        <html>
        <head>
        </head>
        <body>
        <p>%s</p>
        <p>%s</p>
        %s
        </body>
        </html>
        """%(content1,content2,content3)
        '''
        message = """From: %s <%s>
To: %s <%s>
Mime-Version: 1.0
Content-Type: text/html;charset=UTF-8
Content-Transfer-Encoding:base64
Subject: =?utf-8?B?%s?=

%s
""" % (s_email, s_email, r_email, r_email, base64.b64encode(mail_title), encode_content)
        sendmail(domain, s_email, s_passwd, r_email, message, logfh, port)
        '''try:
            smtp = smtplib.SMTP()
            smtp.set_debuglevel(0)
            smtp.connect('smtp.%s'%(domain), 587)
            #smtp.connect('smtp.%s'%(domain), 25)
            #smtp.helo()
            smtp.starttls()
            #smtp.esmtp_features['auth'] = 'LOGIN DIGEST-MD5 PLAIN'
            smtp.login(s_email,s_passwd)
            smtp.sendmail(s_email,r_email,message)
            smtp.close()
            logfh.write("%s to %s success\n"%(s_email,r_email))
            #logfh.write("success\n")
            print "%s to %s success"%(s_email,r_email)
        except:
            logfh.write("%s to %s faild\n"%(s_email,r_email))
            #logfh.write("faild\n")
            print "%s to %s faild"%(s_email,r_email)
            pass'''
    logfh.write("==== " + str(datetime.datetime.today()) + " ====\n")
    logfh.close()
    fh.close()
    time.sleep(sleeptime)


# 主程序入口
def main():
    global g_varfile, g_contentfile, g_titlefile, g_delaytime, g_log_folder, g_frommail, g_smtp, g_passwd, g_columns

    parse_args()

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.info('==================================================')
    logger.info('变量文件:        %s' % g_varfile)
    logger.info('变量所在列:      %s' % g_columns)
    logger.info('邮件主题文件:     %s' % g_titlefile)
    logger.info('邮件内容文件:     %s' % g_contentfile)
    logger.info('邮件间隔时间:     %s' % g_delaytime)
    logger.info('log folder:     %s' % g_log_folder)
    logger.info('==================================================')

    if not os.path.isdir(g_log_folder):
        os.mkdir(g_log_folder)


# 程序起始
if __name__ == '__main__':
    main()
