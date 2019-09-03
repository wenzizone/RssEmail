#! /usr/bin/env python
# -*- coding:utf-8 -*-

import csv
import sys
import os
import mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import parseaddr, formataddr
import base64
import time
import datetime
import argparse
import logging
import chardet
import random
from jinja2 import Environment, FileSystemLoader
from sendmail_worker import *


# global variables
g_varfile = ''
g_contentfile = ''
g_titefile = ''
g_delaytime = ''
g_frommail = 'root@localhost'
g_smtp = ''
g_smtpuser = ''
g_passwd = ''
g_columns = ''
g_alias = ''
g_port = 25
g_log_folder = os.path.join(os.path.split(
    os.path.realpath(sys.argv[0]))[0], 'log')


# 解析传进来的参数
def parse_args():
    global g_varfile, g_contentfile, g_titlefile, g_delaytime, g_log_folder, g_frommail, g_smtp, g_passwd, g_columns, g_port, g_alias, g_smtpuser

    parser = argparse.ArgumentParser(description='邮件群发系统')
    parser.add_argument('--file', nargs='?', required=True, help='变量文件')
    parser.add_argument('--content', nargs='?', required=True, help='邮件内容文件')
    parser.add_argument('--title', nargs='?', required=True, help='邮件标题文件')
    parser.add_argument('-t', nargs='?', required=False,
                        help='每封邮件间隔时间,如-t 30,60')
    parser.add_argument('--alias', nargs='?', required=False,
                        help='发件人别名，如果为空,默认使用邮件地址')
    parser.add_argument('--from', nargs='?', required=False, help='发件人邮件地址')
    parser.add_argument('--smtp', nargs='?', required=False, help='发件邮件服务器地址')
    parser.add_argument('--user', nargs='?', required=False, help='发送邮件服务器登录账号')
    parser.add_argument('--passwd', nargs='?',
                        required=False, help='发件邮件服务器登录密码')
    parser.add_argument('--port', nargs='?',
                        required=False, help='发件邮件服务器端口')
    parser.add_argument('-c', nargs='?', required=False,
                        help='变量所在列,0列为接收人邮件地址')
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
    if args['smtp_user'] != None:
        g_smtpuser = args['smtp_user']
    if args['passwd'] != None:
        g_passwd = args['passwd']
    if args['c'] != None:
        g_columns = args['c']
    if args['port'] != None:
        g_port = args['port']
    if args["alias"] != None:
        g_alias = args["alias"]


# 读取变量文件，获取收件人地址和所有变量
def parse_var_file():
    global g_varfile, g_delaytime, g_columns, g_frommail, g_smtp, g_passwd, g_port, g_alias

    columns_array = g_columns.split(',')

    with open(g_varfile) as fp:
        for line in fp:
            dic_vars = {}
            #time.sleep(float(generate_random_sleeptime()))  # 休眠间隔时间
            line_array = line.split(',')
            to_mail = line_array[0]
            # 设置变量对应的字段，用来替换模板文件中对应的变量位置
            for i in columns_array:
                msg_code = chardet.detect(line_array[int(i)])

                if msg_code["encoding"] == "GB2312":
                    dic_vars[
                        'var' + i] = line_array[int(i)].decode('gbk')
                elif msg_code["encoding"] == "utf-8":
                    dic_vars[
                        'var' + i] = line_array[int(i)].decode('utf-8')
                else:
                    dic_vars['var' + i] = line_array[int(i)]

            email_title = create_title(dic_vars)
            email_message = create_message(dic_vars)

            # print "email_tile: %s" % email_title
            # print "email_message: %s" % email_message

            # 拼接sendmail用的message，包含header和content
            msg = MIMEMultipart()
            if g_alias:
                msg['From'] = formataddr(
                    (Header(g_alias, 'utf-8').encode(), g_frommail))
            else:
                msg['From'] = g_frommail
            msg['To'] = to_mail
            msg['Subject'] = Header(email_title, charset='UTF-8')

            # 添加邮件内容
            txt = MIMEText(email_message, _subtype='plain',  _charset='UTF-8')
            # 添加html的邮件内容
            #txt = MIMEText(email_message,_subtype='html',  _charset='UTF-8')
            msg.attach(txt)

            # 准备发送邮件
            sendmail.delay(
                jason.dumps({
                    'mail_to':to_mail,
                    'mail_msg': msg,
                    'mail_from': g_frommail,
                    'smtp_port': g_port,
                    'smtp_server': g_smtp,
                    'smtp_user': g_smtpuser,
                    'smtp_pass': g_passwd,
                    'send_dely': float(generate_random_sleeptime())
                    })
                )


# 从模板文件生成邮件主题
def create_title(vars):
    global g_titlefile

    THIS_DIR = os.path.dirname(g_titlefile)
    This_file = os.path.basename(g_titlefile)

    # Create the jinja2 environment.
    # Notice the use of trim_blocks, which greatly helps control whitespace.
    j2_env = Environment(loader=FileSystemLoader(THIS_DIR),
                         trim_blocks=True)

    # print vars
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
    msg = j2_env.get_template(This_file).render(vars)
    return msg
    # return base64.b64encode(msg)


# 从给定发送邮件间隔时间随机生成具体的间隔秒数
def generate_random_sleeptime():
    global g_delaytime

    delay_array = g_delaytime.split(',')

    return random.randrange(int(delay_array[0]), int(delay_array[1]))


# 日志功能
def logs(level, msg):
    global g_log_folder

    msg_code = chardet.detect(msg)

    if msg_code["encoding"] == "GB2312":
        msg = msg.decode('gbk').encode("utf-8")

    LEVEL = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    # print datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if level == 0:
        fhd = open(g_log_folder + '/debug.log', 'ab+')
    elif level == 3:
        fhd = open(g_log_folder + '/stderr.log', 'ab+')
    else:
        fhd = open(g_log_folder + '/stdout.log', 'ab+')

    fhd.write("%s %-8s %s\n" %
              (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), LEVEL[level], msg))

    fhd.close()
    #log.log(level, msg)
    # if level == "debug":
    #     logger.debug(msg)
    # elif level == "err":
    #     logger.error(msg)
    # else:
    #     logger.info(msg)



# 主程序入口
def main():
    global g_varfile, g_contentfile, g_titlefile, g_delaytime, g_log_folder, g_frommail, g_smtp, g_passwd, g_columns, g_smtpuser

    parse_args()

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.info('==================================================')
    logger.info('变量文件:       %s' % g_varfile)
    logger.info('变量所在列:      %s' % g_columns)
    logger.info('邮件主题文件:     %s' % g_titlefile)
    logger.info('邮件内容文件:     %s' % g_contentfile)
    logger.info('邮件间隔时间:     %s' % g_delaytime)
    logger.info('发件人邮件地址:   %s' % g_frommail)
    logger.info('发送邮件服务器地址:  %s' % g_smtp)
    logger.info('发送邮件服务器登录账号: %s' % g_smtpuser)
    logger.info('发送邮件服务器端口:  %s' % g_port)
    logger.info('log folder: %s' % g_log_folder)
    logger.info('==================================================')

    if not os.path.isdir(g_log_folder):
        os.mkdir(g_log_folder)

    parse_var_file()


# 程序起始
if __name__ == '__main__':
    main()
