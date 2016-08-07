# -*- coding: utf-8 -*-
# FILE: runXFOIL_alphaSweep.py
#Run with Python 2.7.12
#XFoil needs to be in same folder as Foil Data
# Foils Require selig Parsing before running XFoil 

import time 
import subprocess as sp
import os
import sys
import string

def frange(start, stop, step):
    i = start
    while i < stop:
       yield i
       i += step
 
def issueCmd(cmd,echo=True):
    ps.stdin.write(cmd+'\n')
    ps.stdin.flush()
    if echo:
        print (cmd)

startupinfo = sp.STARTUPINFO()
startupinfo.dwFlags |= sp.STARTF_USESHOWWINDOW

os.chdir('C:\\Users\Aniru_000\Desktop\TD-1\Airfoil\s1223\\airfoil\completed\Flat_bot')
for file in os.listdir(os.getcwd()):
    if file.endswith(".dat"):
            

        ps = sp.Popen(['xfoil.exe'],
                      stdin=sp.PIPE,
                      stdout=None,
                      stderr=None,
                      startupinfo=startupinfo)
         
         
        issueCmd('LOAD '+ file)
         
        issueCmd('GDES')  # enter GDES menu
        time.sleep(0.05)
        issueCmd('CADD')  # add points at corners
        time.sleep(0.5)
        issueCmd('')      # accept default inpu
        #time.sleep(0.05)
        issueCmd('')      # accept default input
        issueCmd('')      # accept default input
        issueCmd('')      # accept default input
        issueCmd('MDES')
        time.sleep(0.05)
        issueCmd('FILT')
        time.sleep(0.5)
        issueCmd('EXEC')
        time.sleep(0.5)
        issueCmd('') 
        issueCmd('PANEL') # regenerate paneling
        time.sleep(0.5)
        issueCmd('OPER')
        issueCmd('ITER 70')
        time.sleep(0.05)
        issueCmd('RE 100000')
        time.sleep(0.05)
        issueCmd('VISC 100000')
        time.sleep(0.05)
        issueCmd('PACC')
        time.sleep(0.5)
        issueCmd('AirfoilPolars/'+ file)
        time.sleep(0.5)
        issueCmd('')
        for aoa in frange(-6,10,0.5):
                issueCmd('ALFA %7.4f' % (aoa,))
                time.sleep(1.2)
        issueCmd('PACC')
        time.sleep(2)
        issueCmd('')
        issueCmd('QUIT')
