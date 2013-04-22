#! /usr/bin/env python
# -*- coding:utf-8 -*-  

import csv
import sys,os,random
import smtplib,base64

print len(sys.argv)
if len(sys.argv) != 2:
    sys.exit('Usage: rssemail.py emailfile')

emailfile = sys.argv[1]


def get_random_file_content(file,contentposition):
    fh = open(file, 'rb')
    fn_size = os.stat(file)[6]
    pos = (fh.tell() + random.randint(0,fn_size)) % (fn_size)
    if contentposition == 't':
        contentpos = 2
    elif contentposition == 'ca':
        contentpos = 3
    elif contentposition == 'cb':
        contentpos = 4
    elif contentposition == 'cc':
        contentpos =5

    try:
        fh.seek(pos)
        csvfh = csv.reader(fh)
        csvfh.next()
        while True:
            tmp = csvfh.next()
            #print len(tmp)
            if len(tmp) != 8:
                continue
            line_content = tmp[contentpos]
            #print line_content
            if len(line_content):
                break
            else:
                continue
    except EOFError:
        pass

    #csvfh.close()
    fh.close()
    #print line_content
    return line_content

mail_title = get_random_file_content(emailfile, 't')
content1 = get_random_file_content(emailfile, 'ca')
content2 = get_random_file_content(emailfile, 'cb')
content3 = get_random_file_content(emailfile, 'cc')

# main 
file = csv.reader(open(emailfile))

for lines in file:
    s_email = lines[0]
    s_passwd = lines[1]
    r_email = lines[6]
    r_passwd = lines[7]
    if s_email == '':
        continue
    tmp= s_email.split('@')
    if len(tmp) < 2:
        continue
    domain = tmp[1]
    print s_email,",",domain,",",s_passwd,",",r_email

    message = '''From: %s <%s>
    To: %s <%s>
    MIME_version: 1.0
    Content-type: text/html
    Subject: %s

    <html>
    <head>
    </head>
    <body>
    <p>%s</p>
    <p>%s</p>
    %s
    </body>
    </html>
    '''%(s_email,s_email,r_email,r_email,mail_title,content1,content2,content3)
    #print message
    smtp = smtplib.SMTP()
    smtp.set_debuglevel(0)
    smtp.connect('smtp.%s'%(domain))
    #smtp.helo()
    smtp.login(s_email,s_passwd)

    #smtpobj = smtplib.SMTP('smtp.%s'%(domain), 25)
    #smtpobj.ehlo()
    #smtpobj.starttls()
    #smtpobj.login(s_email,s_passwd)
    smtp.sendmail(s_email,r_email,message)