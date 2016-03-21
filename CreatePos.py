# -*- coding:utf8 -*-
import os
import time
import tempfile
import codecs
import platform

import threading, subprocess
import sys
import shutil
import json
import functools


if platform.system() == 'Windows':
    import win32com.client
    g_autoit = win32com.client.Dispatch("AutoItX3.Control")
    import ctypes, win32con, ctypes.wintypes, win32gui
    from win32api import GetSystemMetrics

##abs_dir = 'E:\\WORK\\quality_control\\SET\\XFATest\\log\\foxit\\0首批要检查的文档\\foxit脚本执行时间长\\ACCOUNTS.PDF'
##os.mkdir(abs_dir)
##asdf

TEST_ONLY_ONE_PAGE = False
TEST_COVERAGE = False
ADOBE_ACROBAT_PATH = '"D:\\Program Files (x86)\\Adobe\\Acrobat 11.0\\Acrobat\\Acrobat.exe"'
FXQA_DEMO_PATH = '"Win32\\Debug\\XFATest_VC12.exe"'
DRRUNN_PATH = 'D:\\DynamoRIO-Windows-6.0.0-6\\bin32\\drrun.exe'
DRRUNN_LOG_DIR = 'E:\\work\\quality_control\\fxcore\\branch\\XFATest\\log\\cov'

EXIT = False
TESTFILE_FOLDER = u'E:\\WORK\\quality_control\\SET\\XFATest\\XFA_testfiles'
#TESTFILE_FOLDER = u'E:\\adobe_test'
POS_FOLDER = u'E:\\tem\\pos'
g_fp_runned = codecs.open('log/runned.txt', 'a', 'utf8')
g_fp_err = codecs.open('log/errpdf.txt', 'a', 'utf8')
g_time_id = 0

g_currnt_testfile = ''
g_test_process = ''

g_adobe_opened = True


def mkdir(dir_path):
    dir_path = dir_path.replace('\\', '/')
    dir_list = dir_path.split('/')
    if platform.system() == 'Windows':
        if dir_list[0][1] == ':':
            dir_list[0] = dir_list[0].replace(':', ':/')
    else:
        if dir_list[0] == '':
            dir_list[0] = '/'
    abs_dir = dir_list[0]
    dir_index = 0
    while 1:
        if os.path.exists(abs_dir) == False:
            os.mkdir(abs_dir)
##        else:
##            print('exist:' + abs_dir)
        if dir_index >= len(dir_list):
            break
        try:
            abs_dir = os.path.join(abs_dir, dir_list[dir_index+1])
        except:
            break
        dir_index = dir_index + 1

        
class XFA_ELEMENT_TYPE:
  def __init__(self):
    self.Subform = 126
    self.Text = 77
    self.ChoiceList = 39
    self.TextEdit = 210
    self.Button = 72
    self.NumericEdit = 185
    self.DateTimeEdit = 115
    self.CheckButton = 13

def ImageCatch(out_filename, range_catch):
    cmd = 'ImageProcessing -g ' + '-m ' + range_catch + ' -o ' + '\"' + out_filename + '\"'
    buf = os.popen(cmd).read()
    print(buf)

            
class StatusMonitor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.is_break = False

    def run(self):
        global g_time_id
        while not self.is_break:
            g_time_id = g_time_id + 1
            time.sleep(10)
            if g_time_id > 180:
                g_fp_err.write('LONG TIME:')
                g_fp_err.write(g_currnt_testfile)
                g_fp_err.write('\n')
                g_fp_err.flush()
                if platform.system() != 'Windows':
                    os.popen('pkill XFATest')
                else:
                    os.popen('taskkill /F /IM XFATest.exe')
                break
            #os.popen('C:\\Windows\\System32\\taskkill /F /IM WerFault.exe')

    def stop(self):
        self.is_break = True
        

def ClearLogSpace():
  for root, dirs, files in os.walk(TEST_LOG_PATH):
    for filename in files:
      if os.path.splitext(filename)[1] == '.txt':
        os.remove(os.path.join(root, filename))


def RunFXQA(filepath, save_folder):
    savefolder = os.path.dirname(filepath.split(TESTFILE_FOLDER)[1])
    savefolder = POS_FOLDER + savefolder
    savepath = savefolder + '\\' + os.path.splitext(os.path.basename(filepath))[0] + '.log'
##    savepath = 
##    print(savepath)
##    savepath = os.path.splitext(savepath)[0] + '.log'
##    print(savefolder)
##    llllllllll


    if not os.path.exists(savefolder):
        mkdir(savefolder)

    if TEST_COVERAGE == True:
        cmd = '%s -t drcov -logdir %s -- %s -f "%s" -s "%s"' \
              % (DRRUNN_PATH, DRRUNN_LOG_DIR, FXQA_DEMO_PATH, filepath, savepath)
    else:
        cmd = '%s -f "%s" -w "%s"' \
              % (FXQA_DEMO_PATH, filepath, savepath)
    print(cmd)


    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    global g_test_process
    g_test_process = p
    for line in iter(p.stdout.readline, b''):
        print(line)
        if line.decode('utf8').find('Save End') != -1:
            p.kill()
        if line.decode('utf8').find('Crash ERROR') != -1:
            print(line)
            g_fp_err.write(line.decode('utf8').split('ERROR:')[1])
            g_fp_err.write('\n')
            g_fp_err.flush()
        if line.decode('utf8').find('NOT XFA') != -1:
            p.kill()
            return False
    return True

def CreateMsgBoxLog(logpath):
    fp = codecs.open(os.path.join(logpath, 'msgbox.xml'), 'w', 'utf8')
    fp.write('<xml>')
    return fp

def CloseMsgBoxLog(msglog_fp):
    msglog_fp.write('</xml>\n')
    msglog_fp.close()    





def RunTest(testfile_folder, save_folder='log'):
    fp_runned = codecs.open('log/runned.txt', 'r', 'utf8')
    runned_list = fp_runned.readlines()
    for root, dirs, files in os.walk(testfile_folder):
        for filename in files:
            sufix = os.path.splitext(filename)[1][1:]
            if sufix.upper() != 'PDF':
                continue
            filepath = os.path.join(root, filename)
            if filepath + '\n' in runned_list:
                continue
            print(filepath)
            global g_currnt_testfile
            g_currnt_testfile = filepath

            global g_time_id
            g_time_id = 0

            status_monitor = StatusMonitor()
            status_monitor.start()
            #filepath = 'C:\\Users\\Administrator\\Desktop\\xfa\\Untitled5.pdf'
            if RunFXQA(filepath, os.path.join(save_folder, 'foxit')):
##                test
##                RunJSAdobe(filepath, save_folder + '\\adobe')
##                CompareResult(filepath, save_folder)
##                test
##                g_fp_runned.write(filepath)
##                g_fp_runned.write('\n')
##                g_fp_runned.flush()

                global g_adobe_opened
                g_adobe_opened = False

                status_monitor.stop()
                
        

def main():
  #ClearLogSpace()
  #RunTest_Adobe()
##  RunFXQA(testfile_folder)
    RunTest(TESTFILE_FOLDER)

if __name__ == '__main__':
    main()
  
