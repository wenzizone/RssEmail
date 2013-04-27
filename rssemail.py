#! /usr/bin/env python
# -*- coding:utf-8 -*-  

import csv
import sys,os,random
import smtplib,base64
import time,datetime

#print len(sys.argv)
if len(sys.argv) == 4:
    delaytime = float(0)
elif len(sys.argv) == 6:
    delayoptions = sys.argv[4]
    delaytime = float(sys.argv[5])
    if delayoptions == '-m':
        delaytime = delaytime*60
    elif delayoptions == '-h':
        delaytime = delaytime*60*60
    else:
        sys.exit('the 5th option should be -m or -h')
else:
    sys.exit('''
Usage: rssemail.py emailfile -time time (-delaytime time)
    -time means : -m -h 
    -m minutes
    -h hours

    -delaytime : -m -h
    -m minutes
    -h hours
    ''')

logdir = '/var/log/blogmail'

emailfile = sys.argv[1]

options = sys.argv[2]
sleeptime = float(sys.argv[3])

if options == '-m':
    sleeptime = sleeptime*60
elif options == '-h':
    sleeptime = sleeptime*60*60
else:
    sys.exit('the third option should be -m or -h')


# 随机获得csv文件每列的内容
def get_random_file_content(mailfile,contentpos,maxpos):
    fh = open(mailfile, 'rb')
    fn_size = os.stat(mailfile)[6]
    pos = (fh.tell() + random.randint(0,fn_size)) % (fn_size)
    line_content = ''
    try:
        fh.seek(pos)
        csvfh = csv.reader(fh)
        csvfh.next()
        while True:
            tmp = csvfh.next()
            #print len(tmp)
            if len(tmp) != maxpos:
                continue
            line_content = tmp[contentpos]
            #print line_content
            if len(line_content):
                break
            else:
                continue
    except:
        fh.seek(0)
        pass
    while 1:
        if len(line_content):
            break
        else:
            line_content = get_random_file_content(mailfile,contentpos,maxpos)

    #csvfh.close()
    fh.close()
    #print line_content
    return line_content

# 随机同时获取csv文件5，6列内容
def get_random_56_content(mailfile,maxpos,contentpos = [4,5]):
    fh = open(mailfile, 'rb')
    fn_size = os.stat(mailfile)[6]
    pos = (fh.tell() + random.randint(0,fn_size)) % (fn_size)
    line_content = ''
    mail_title = ''
    try:
        fh.seek(pos)
        csvfh = csv.reader(fh)
        csvfh.next()
        while True:
            tmp = csvfh.next()
            #print len(tmp)
            if len(tmp) != maxpos:
                continue
            mail_title = tmp[contentpos[0]]
            line_content = tmp[contentpos[1]]
            #print line_content
            if len(line_content) and len(mail_title):
                break
            else:
                continue
    except:
        fh.seek(0)
        pass

    while 1:
        if len(line_content) and len(mail_title):
            break
        else:
            (line_content,mail_title) = get_random_56_content(mailfile,maxpos)

    #csvfh.close()
    fh.close()
    return [line_content,mail_title]

#def sendmail():


# main
time.sleep(delaytime)
if os.path.exists(logdir) == False:
        os.mkdir(logdir)
        #pass
logfile = os.path.basename(emailfile)
logfile = logfile.split('.')[0]
logfile = logdir+'/'+logfile+'.log'
print logfile
while True:
    
    fh = open(emailfile)
    csvfile = csv.reader(fh)
    logfh = open(logfile, 'w')
    logfh.write("==== "+str(datetime.datetime.today())+" ====\n")
    logfh.close()
    logfh = open(logfile, 'a')

    for lines in csvfile:
        s_email = lines[0]
        s_passwd = lines[1]
        r_email = lines[2]
        r_passwd = lines[3]

        #mail_title = get_random_file_content(emailfile, 4, len(lines))
        (content,mail_title) = get_random_56_content(emailfile,len(lines))
        print mail_title
        for i in range(6,len(lines)):
            content_tmp = get_random_file_content(emailfile, i, len(lines))
            content = content + content_tmp

        if s_email == '':
            continue
        tmp= s_email.split('@')
        if len(tmp) < 2:
            continue
        if tmp[1] == 'hotmail.com':
            domain = 'live.com'
        else:
            domain = tmp[1]

        #print s_email,",",domain,",",s_passwd,",",r_email
        #print mail_title,'---',content
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
"""%(s_email,s_email,r_email,r_email,base64.b64encode(mail_title),encode_content)

        print message
        try:
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
            pass
    logfh.write("==== "+str(datetime.datetime.today())+" ====\n")
    logfh.close()
    fh.close()
    time.sleep(sleeptime)
