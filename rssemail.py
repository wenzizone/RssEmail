#! /usr/bin/env python
# -*- coding:utf-8 -*-  

import csv
import sys,os,random
import smtplib,base64

print len(sys.argv)
if len(sys.argv) != 6:
    sys.exit('Usage: rssemail.py emailfile titlefile content1file content2file content3file')

emailfile = sys.argv[1]
titlefile = sys.argv[2]
content1file = sys.argv[3]
content2file = sys.argv[4]
content3file = sys.argv[5]

def get_random_file_content(file):
    fh = open(file,'rb')
    fn_size = os.stat(file)[6]
    pos = (fh.tell() + random.randint(0,fn_size)) % (fn_size)
    try:
        fh.seek(pos)
        fh.readline()
        while True:
            line_content = fh.readline()
            if line_content.split():
                break
            else:
                continue
    except EOFError:
            pass


    fh.close()
    return line_content


mail_title = get_random_file_content(titlefile)

# main 
file = csv.reader(open(emailfile))

for s_email,s_passwd,r_email,r_passwd in file:
    if s_email == '':
        continue
    tmp= s_email.split('@')
    if len(tmp) < 2:
        continue
    domain = tmp[1]
    print s_email,",",domain,",",s_passwd,",",r_email
    smtpobj = smtplib.SMTP('smtp.%s'%domain)
    smtpobj.login(s_email,s_passwd)
    




'''while 1:
    lines = file.readlines(1000)
    if not lines:
        break
    for line in lines:
        (a,b,c,d,e,f,g,h) = line.split(',')
        print a
        '''