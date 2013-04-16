#! /usr/bin/env python
# -*- coding:utf-8 -*-  

import csv
file = csv.reader(open("ian_testing_100emails-1.csv"))

for a,b,c,d,e,f,g,h in file:
    print c
'''while 1:
    lines = file.readlines(1000)
    if not lines:
        break
    for line in lines:
        (a,b,c,d,e,f,g,h) = line.split(',')
        print a
        '''