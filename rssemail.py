#! /usr/bin/env python
# -*- coding:utf-8 -*-  

import csv
import sys,os,random
import smtplib,base64

print len(sys.argv)
if len(sys.argv) != 2:
    sys.exit('Usage: rssemail.py emailfile')

emailfile = sys.argv[1]


def get_random_file_content(file,contentpos,maxpos):
    fh = open(file, 'rb')
    fn_size = os.stat(file)[6]
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
            line_content = get_random_file_content(file,contentpos,maxpos)

    #csvfh.close()
    fh.close()
    #print line_content
    return line_content
'''
mail_title = get_random_file_content(emailfile, 't')
content1 = get_random_file_content(emailfile, 'ca')
content2 = get_random_file_content(emailfile, 'cb')
content3 = get_random_file_content(emailfile, 'cc')
'''
# main 
file = csv.reader(open(emailfile))

for lines in file:
    s_email = lines[0]
    s_passwd = lines[1]
    r_email = lines[2]
    r_passwd = lines[3]

    mail_title = get_random_file_content(emailfile, 4, len(lines))
    content = ''
    for i in range(5,len(lines)-1):
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

    print s_email,",",domain,",",s_passwd,",",r_email,'---',mail_title,'===',content
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

    #print message
    try:
        smtp = smtplib.SMTP()
        smtp.set_debuglevel(1)
        smtp.connect('smtp.%s'%(domain), 25)
        #smtp.helo()
        smtp.starttls()
        #smtp.esmtp_features['auth'] = 'LOGIN DIGEST-MD5 PLAIN'
        smtp.login(s_email,s_passwd)

        #smtpobj = smtplib.SMTP('smtp.%s'%(domain), 25)
        #smtpobj.ehlo()
        #smtpobj.starttls()
        #smtpobj.login(s_email,s_passwd)
        smtp.sendmail(s_email,r_email,message)
        smtp.close()
    except:
        pass