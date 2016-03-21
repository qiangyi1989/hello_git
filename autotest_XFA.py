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
ADOBE_ACROBAT_PATH = '"D:\\Adobe\\Acrobat 11.0\\Acrobat\\Acrobat.exe"'
FXQA_DEMO_PATH = '"Win32\\Debug\\XFATest_VC10.exe"'
DRRUNN_PATH = 'D:\\DynamoRIO-Windows-6.0.0-6\\bin32\\drrun.exe'
DRRUNN_LOG_DIR = 'E:\\work\\quality_control\\fxcore\\branch\\XFATest\\Win32\\Debug\\cov'

EXIT = False
TESTFILE_FOLDER = u'F:\\test'
#TESTFILE_FOLDER = u'E:\\adobe_test'
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

def StrToHex(s):
    lst = []
    for ch in s:
        hv = hex(ord(ch)).replace('0x', '')
        z = '0'
        if len(hv) == 1:
            hv = '0'+hv
        if len(hv) < 4:
            for i in range(0, (3 - len(hv))):
                z = z + '0'
            hv = z + hv
        hv = '\\u' + hv
        lst.append(hv)
    return functools.reduce(lambda x,y:x+y, lst)
        
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

class Hotkey(threading.Thread):
    def run(self):  
        global EXIT
        user32 = ctypes.windll.user32
        if not user32.RegisterHotKey(None, 99, win32con.MOD_ALT, win32con.VK_F3):
            raise
        try:  
            msg = ctypes.wintypes.MSG()  
            print(msg)  
            while user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:  
                if msg.message == win32con.WM_HOTKEY:  
                    if msg.wParam == 99:
                        EXIT = True  
                        return  
                user32.TranslateMessage(ctypes.byref(msg))  
                user32.DispatchMessageA(ctypes.byref(msg))  
        finally:
            user32.UnregisterHotKey(None, 1)
            
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

def WaitWindow(key, timeout=30):
  t = 0
  while 1:
    if g_autoit.WinActive(key):
      return True
      #print g_autoit.WinGetText(key)
    time.sleep(1)
    t += 1
    if t > timeout:
      return False

def ContainStr(key, window_key):
  win_str = g_autoit.WinGetText(window_key)
  if win_str.find(key) != -1:
    return True
  return False

def FoucsControl(control_key, window_key, timeout=30):
  t = 0
  while 1:
      foucs_ctl = g_autoit.ControlGetFocus(window_key)
      if foucs_ctl == control_key:
        return True
      g_autoit.Send('{TAB}')
      t += 1
      if t > timeout:
        return False
  return False

def SelectSaveType(save_type, window_key, timeout=30):
  t = 0
  while 1:
    if ContainStr(save_type, window_key):
      return True
    g_autoit.Send('{DOWN}')
    t += 1
    if t > timeout:
      break
  return False

def HandleAdobeMsgBox(msglog_fp = None):
    os.popen('taskkill /FI "WINDOWTITLE eq autotest.pdf - Adobe Acrobat Pro"')
    if ContainStr('FXQAAT OPEN', 'Adobe Acrobat'):
        g_autoit.Send('{ENTER}')
        return 2 # Open test file

    if g_autoit.WinExists("Full Screen"):
        if g_autoit.WinActive('Full Screen'):
            if FoucsControl('Button1', 'Full Screen'):
                g_autoit.Send('{ENTER}')
                return 0

    if g_autoit.WinExists('Print'):
        if g_autoit.WinActive('Print'):
            g_autoit.Send('{ESC}')
            return 0

    if g_autoit.WinExists('Save As'):
        if g_autoit.WinActive('Save As'):
            if FoucsControl('Button3', 'Save As'): # Cancel
                g_autoit.Send('{ENTER}')
            return 0

    if g_autoit.WinExists('Save PDF File As'):
        if g_autoit.WinActive('Save PDF File As'):
            if FoucsControl('Button2', 'Save PDF File As'): # Cancel
                g_autoit.Send('{ENTER}')
            return 0

    if g_autoit.WinExists('Error: Nothing Done'): # Download ERROR.
        if g_autoit.WinActive('Error: Nothing Done'):
            if FoucsControl('Button1', 'Error: Nothing Done'): # OK
                g_autoit.Send('{ENTER}')
            return 0

    if g_autoit.WinExists('Export Form Data As'): # Export Data
        if g_autoit.WinActive('Export Form Data As'):
            if FoucsControl('Button3', 'Export Form Data As'): # Cancel
                g_autoit.Send('{ENTER}') 
            return 0

    if g_autoit.WinExists('Reading Untagged Document'): 
        if g_autoit.WinActive('Reading Untagged Document'):
            if FoucsControl('Button7', 'Reading Untagged Document'): # Cancel
                g_autoit.Send('{ENTER}') 
            return 0

    if g_autoit.WinExists('Send Email'): 
        if g_autoit.WinActive('Send Email'):
            if FoucsControl('Button7', 'Send Email'): # Cancel
                g_autoit.Send('{ENTER}') 
            return 0

    if g_autoit.WinExists('Calculation Override'): 
        if g_autoit.WinActive('Calculation Override'):
            g_autoit.Send('{ENTER}') 
            return 0
    
        
    if ContainStr('Do you want to save changes to', 'Adobe Acrobat'):
        if FoucsControl('Button2', 'Adobe Acrobat'):
            g_autoit.Send('{ENTER}')
            return 0
        
    if ContainStr('already exists. Do you want to overwrite it', 'Adobe Acrobat'):
        if FoucsControl('Button1', 'Adobe Acrobat'):
            g_autoit.Send('{SPACE}')
            g_autoit.Send('{ENTER}')
            return 0

    if ContainStr('password', 'Warning: JavaScript Window - ECMAScript'):
        if FoucsControl('Button2', 'Warning: JavaScript Window - ECMAScript'): # Cancel
            g_autoit.Send('{ENTER}')
            return 3

    if g_autoit.WinExists('JavaScript Window'): 
        if g_autoit.WinActive('JavaScript Window'):
            if FoucsControl('Button3', 'JavaScript Window'): # Cancel
                g_autoit.Send('{ENTER}') 
            return 0

    if ContainStr('please click Submit to ensure your data will be collected correctly', 'Adobe Acrobat'):
        if FoucsControl('Button1', 'Adobe Acrobat'):
            g_autoit.Send('{SPACE}')
            g_autoit.Send('{ENTER}')
            return 0
    if ContainStr('not supported with this form', 'Warning: JavaScript Window - Warning: Adobe Reader Version'):
        if FoucsControl('Button2', 'Warning: JavaScript Window - Warning: Adobe Reader Version'):
            g_autoit.Send('{ENTER}')
            return 0
    if ContainStr('version', '[CLASS:#32770]'):
        g_autoit.Send('{ENTER}')
        return 0
    if ContainStr('If you do not trust the site', 'Security Warning'):
        if FoucsControl('Button3', 'Security Warning'):
            g_autoit.Send('{ENTER}')
            return 1 # open web browser.
    if ContainStr('If you trust this site', 'Security Warning'):
        if FoucsControl('Button3', 'Security Warning'):
            g_autoit.Send('{ENTER}')
            return 1 # open web browser.
    if ContainStr('Trusted Certificates', 'Trusted Certificates Update'):
        if FoucsControl('Button2', 'Trusted Certificates Update'):
            g_autoit.Send('{ENTER}')
            return 0

##    if ContainStr('must be prepared for reading', 'Reading Untagged Document'):
##        g_autoit.Send('{ESC}')
##        return 0
    if ContainStr('NotAllowedError', 'Warning: JavaScript Window - '):
        g_autoit.Send('{ENTER}')
        return 0
    if ContainStr('Acrobat does not allow connection', 'Security Block'):
        if FoucsControl('Button3', 'Security Block'):
            g_autoit.Send('{ENTER}')
            return 0
    if ContainStr('Do you want to save changes', 'Adobe Acrobat'):
        if FoucsControl('Button3', 'Adobe Acrobat'):
            g_autoit.Send('{ENTER}')
            return 10 # Save Error, ATTest END.

    if g_autoit.WinActive("Adobe Acrobat"):
        if msglog_fp != None:
            msglog_fp.write('<msg>')
            msglog_fp.write(g_autoit.WinGetText("Adobe Acrobat"))
            msglog_fp.write('</msg>\n')
            msglog_fp.flush()
        g_autoit.Send('{ENTER}')
        return 0

    if g_autoit.WinActive("Warning: JavaScript Window - "):
        g_autoit.Send('{ENTER}')
        return 0
  
    if ContainStr('FXQAAT END', 'Adobe Acrobat'):
        g_autoit.Send('{ENTER}')
        return 10 # ATTest END.
    if g_autoit.WinActive("Adobe Acrobat"):
        g_autoit.OPT("WinDetectHiddenText", 1)
        winText = g_autoit.WinGetText('Adobe Acrobat', '')
        g_autoit.OPT("WinDetectHiddenText", 0)
        winText = ''.join(winText)
        if winText.find('APPCRASH') != -1:
            g_autoit.Send('{ENTER}')
            return 10 # Adobe Crash.
    if g_autoit.WinActive('Security Warning'):
        if FoucsControl('Button3', 'Security Warning'):
            g_autoit.Send('{ENTER}')
            return 1 # open web browser.
    
    if not g_autoit.WinExists('[CLASS:AcrobatSDIWindow]'):
        global g_adobe_opened
        if g_adobe_opened:
            return 10 # Adobe already exit.

    if g_autoit.WinExists("{#32770}"):
        if g_autoit.WinActive('{#32770}'):
            g_autoit.Send('{ENTER}')
            return 0
        
    return 2

def HandleOtherAction(action_id = -1):
    if action_id == 1:
        os.popen('taskkill /IM FireFox.exe /F')
        os.popen('taskkill /IM chrome.exe /F')
        os.popen('taskkill /IM "Internet Explorer.exe" /F')
        return 1
    if action_id == 2: # Open test file.
        while not g_autoit.WinExists('autotest.pdf - Adobe Acrobat Pro'):
            time.sleep(0.5)
            g_autoit.WinClose("autotest.pdf - Adobe Acrobat Pro")
            return 2
    if action_id == 3:
        while not g_autoit.WinExists('autotest.pdf - Adobe Acrobat Pro'):
            time.sleep(0.5)
            g_autoit.WinClose("autotest.pdf - Adobe Acrobat Pro")
            return 3

    os.popen('taskkill /IM FireFox.exe /F')
    os.popen('taskkill /IM chrome.exe /F')
    os.popen('taskkill /IM "Internet Explorer.exe" /F')
    return 0
      
def DoSave(timeout=1):
  t = 0
  while 1:
    g_autoit.Send('{ENTER}')
    time.sleep(1)
    HandleAdobeMsgBox()
    if g_autoit.WinActive("[CLASS:AcrobatSDIWindow]"):
      return True
    t += 1
    if t > timeout:
      break
  return False

def SetSavePath(savepath, filename):
  try:
    os.mkdir(savepath)
  except:
    pass
  #print(os.path.join(savepath, filename))
  filename = filename.replace('#', '_')
  filename = filename.replace('&', '_')
  filename = filename.replace('{', '_')
  filename = filename.replace('}', '_')
  filename = filename.replace('%', '_')
  filename = filename.replace('+', '_')
  g_autoit.Send(os.path.join(savepath, filename))

def WaitSaveEnd(timeout=300):
  t = 0
  while 1:
    g_autoit.Send('^d')
    time.sleep(2)
    HandleAdobeMsgBox()
    if g_autoit.WinActive("Document Properties"):
      return True
    t += 1
    if t > timeout:
      break
    if ContainStr('Insufficient permissions', 'Adobe Acrobat'):
      if FoucsControl('Button2', 'Adobe Acrobat'):
        g_autoit.Send('{ENTER}')
  return False

def WaitSaveAsWindow(timeout=30):
  t = 0
  while 1:
    if g_autoit.WinActive('Save As'):
      return True
      #print g_autoit.WinGetText(key)
    time.sleep(1)
    g_autoit.Send('^+s')
    t += 1
    if t > timeout:
      return False
    
def RunAdobe(filepath, save_folder):
  savepath = save_folder + filepath.split(TESTFILE_FOLDER)[1]
  savepath = savepath.replace('#', '_')
  savepath = savepath.replace('&', '_')
  savepath = savepath.replace('{', '_')
  savepath = savepath.replace('}', '_')
  savepath = savepath.replace('%', '_')
  savepath = savepath.replace('+', '_')
  if not os.path.exists(savepath) or os.path.isfile(savepath):
    mkdir(savepath)
    
  p = subprocess.Popen(ADOBE_ACROBAT_PATH + ' ' + filepath)
  while 1:
    time.sleep(0.5)
    print('Do Handle Adobe MsgBox')
    action_type = HandleAdobeMsgBox()
    HandleOtherAction(action_type)
        
    if g_autoit.WinActive("[CLASS:AcrobatSDIWindow]"):
      g_autoit.WinSetOnTop("[CLASS:AcrobatSDIWindow]", "", 1)
      time.sleep(0.5)
      HandleOtherAction()
      
      g_autoit.WinActive("[CLASS:AcrobatSDIWindow]")
      time.sleep(0.5)
      WaitSaveAsWindow()
      g_autoit.WinSetOnTop("[CLASS:AcrobatSDIWindow]", "", 0)

      if not FoucsControl('Edit1', 'Save As'):
        return
      SetSavePath(savepath, os.path.basename(filepath))

      if not FoucsControl('ComboBox2', 'Save As'):
        return
      if not SelectSaveType('*.png', 'Save As'):
        return
      DoSave()
      HandleOtherAction(HandleAdobeMsgBox())
      WaitSaveEnd()
      break
    time.sleep(1)
  p.kill()

def RunFXQA(filepath, save_folder):
    savepath = save_folder + filepath.split(TESTFILE_FOLDER)[1]
    savepath = savepath.replace('#', '_')
    savepath = savepath.replace('&', '_')
    savepath = savepath.replace('{', '_')
    savepath = savepath.replace('}', '_')
    savepath = savepath.replace('%', '_')
    savepath = savepath.replace('+', '_')

    if not os.path.exists(savepath) or os.path.isfile(savepath):
        mkdir(savepath)

    if TEST_COVERAGE == True:
        cmd = '%s -t drcov -logdir %s -- %s -f "%s" -s "%s"' \
              % (DRRUNN_PATH, DRRUNN_LOG_DIR, FXQA_DEMO_PATH, filepath, savepath)
    else:
        cmd = '%s -f "%s" -s "%s" -w "E:\\tem.log"' \
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

def CreateComparePNG(filepath0, filepath1, savepath):
  cmd = 'ImageProcessing -c "%s" "%s" -o "%s" -f' % (filepath0, filepath1, savepath)
  print(cmd)
  os.popen(cmd)
  
def CompareResult(filepath, save_folder):
    savepath = save_folder + '/compare/' + filepath.split(TESTFILE_FOLDER)[1]
    if not os.path.exists(savepath) or os.path.isfile(savepath):
        mkdir(savepath)

    adobe_savepath = os.path.join(save_folder, 'adobe')
    adobe_savepath = adobe_savepath + "\\" + filepath.split(TESTFILE_FOLDER)[1]

    foxit_savepath = os.path.join(save_folder, 'foxit')
    foxit_savepath = foxit_savepath + "\\" + filepath.split(TESTFILE_FOLDER)[1]

    for root, dirs, files in os.walk(adobe_savepath):
        for filename in files:
            if os.path.splitext(filename)[1] != '.png':
                continue
            adobe_pngpath = os.path.join(root, filename)
            foxit_pngpath = foxit_savepath + '\\' + filename
##            print(adobe_pngpath)
##            print(foxit_pngpath)
            if not os.path.exists(foxit_pngpath):
                g_fp_err.write(filepath)
                g_fp_err.write('\n')
                g_fp_err.flush()
                print('Error Not Found: %s' % foxit_pngpath)
                break
            compare_save_path = savepath + '/' + filename
            CreateComparePNG(adobe_pngpath, foxit_pngpath, compare_save_path)

def SetJSScript(filepath, save_folder):
    js = '''
FXAT_SavePNG = app.trustedFunction( function ()
{

app.beginPriv(); // Explicitly raise privilege
var testDoc = app.openDoc("%s");
app.fullscreen = true;
app.fs.cursor = cursor.visible;
app.alert("FXQAAT OPEN.");
//testDoc.saveAs("/%s.png", "com.adobe.acrobat.png");
//app.alert("FXQAAT END.");
//testDoc.closeDoc();
app.endPriv();
// Additional code may appear below.
});'''

    fp = open('D:\\Adobe\\Acrobat 11.0\\Acrobat\\Javascripts\\a.js', 'w')
    
    js_filepath = '/' + filepath.replace(':\\', '/').replace('\\', '/')
    js_savepath = (save_folder + '\\' + os.path.basename(filepath)).replace(':\\', '/').replace('\\', '/')[:-4]

    fp.write(js % (StrToHex(js_filepath), ''))

    fp.close()

def CalcAdobeSideWidth(pdf_page_width):
    screen_width = GetSystemMetrics(0)
    side_width = (screen_width - pdf_page_width) / 2
    return side_width

def CalcAdobeSideHeight(pdf_page_height):
    screen_height = GetSystemMetrics(1)
    side_height = (screen_height - pdf_page_height) / 2
    return side_height

def CalcAdobeWidgetPos(widget_type, adobe_side_width, adobe_side_height, pdf_widget_rect):
    if adobe_side_width == 0:
        pos_y = adobe_side_height + pdf_widget_rect.top
        pos_x = pdf_widget_rect.left
    else:
        pos_y = pdf_widget_rect.top
        pos_x = adobe_side_width + pdf_widget_rect.left

    if widget_type == 'CheckButton':
        pos_x = pos_x + 10
        pos_y = pos_y + 10
    else:
        pos_x = pos_x + (pdf_widget_rect.width/2)
        pos_y = pos_y + (pdf_widget_rect.height/2)
    return (pos_x, pos_y)
    
class PDFWidgetRect():
    def __init__(self):
        self.left = 0
        self.top = 0
        self.width = 0
        self.height = 0

def GetPDFWidgetRect(widget_rect):
    pdf_widget_rect = PDFWidgetRect()
    pdf_widget_rect.left = float(widget_rect['l'])
    pdf_widget_rect.top = float(widget_rect['t'])
    pdf_widget_rect.width = float(widget_rect['w'])
    pdf_widget_rect.height = float(widget_rect['h'])
    
    return pdf_widget_rect

def DoAdobePageDown():
    #return
    #g_autoit.Send('{ESC}')
    HandleAdobeMsgBox()
    WaitWindow('[CLASS:AcrobatSDIWindow]')
    g_autoit.MouseMove(130, 100)
    g_autoit.MouseClick('left')#kill focus
    g_autoit.Send('{RIGHT}')
    #time.sleep(0.05)
    #g_autoit.MouseMove(105, 100)
    #g_autoit.Send('{CTRLDOWN}')
    #g_autoit.Send('{l}')
    #time.sleep(0.01)
    #g_autoit.Send('{CTRLUP}')
#    if g_autoit.WinExists("Full Screen"):
#        if g_autoit.WinActive('Full Screen'):
#            if FoucsControl('Button1', 'Full Screen'):
#                g_autoit.Send('{ENTER}')
##    g_autoit.Send('{DOWN}')

def DoAdobePageUp():
    HandleAdobeMsgBox()
    WaitWindow('[CLASS:AcrobatSDIWindow]')
    g_autoit.MouseMove(24, 976)
    g_autoit.MouseClick('left')


def DoWidgetAction(json_dic, msgbox_fp=None):
    time_limit = 100
    time_wait = 0
    while 1:
        HandleAdobeMsgBox(msgbox_fp)
        g_autoit.WinActivate("[CLASS:AcrobatSDIWindow]")
        if g_autoit.WinActive("[CLASS:AcrobatSDIWindow]"):
            page_size = json_dic['PageSize'].split('*')
            adobe_side_width = int(CalcAdobeSideWidth(int(page_size[0])))
            adobe_size_height = int(CalcAdobeSideHeight(int(page_size[1])))
            pdf_widget_rect = GetPDFWidgetRect(json_dic['Rect'])
            
            adobe_widget_pos = CalcAdobeWidgetPos(json_dic['Type'], adobe_side_width, adobe_size_height, pdf_widget_rect)
            print('Pos: (%d, %d)' % (adobe_widget_pos[0], adobe_widget_pos[1]))
            if json_dic['Type'] == '':
                return
            elif json_dic['Type'] == 'Button':
                g_autoit.MouseMove(adobe_widget_pos[0], adobe_widget_pos[1])
                g_autoit.MouseClick('left')
                HandleAdobeMsgBox(msgbox_fp)
            elif json_dic['Type'] == 'TextEdit':
                g_autoit.MouseMove(adobe_widget_pos[0], adobe_widget_pos[1])
                g_autoit.MouseClick('left')
                g_autoit.Send('aA4+')
                HandleAdobeMsgBox(msgbox_fp)
            elif json_dic['Type'] == 'CheckButton':
                g_autoit.MouseMove(adobe_widget_pos[0], adobe_widget_pos[1])
                g_autoit.MouseClick('left')
                g_autoit.MouseClick('left')
                g_autoit.MouseClick('left')
                HandleAdobeMsgBox(msgbox_fp)
            elif json_dic['Type'] == 'ChoiceList':
                g_autoit.MouseMove(adobe_widget_pos[0], adobe_widget_pos[1])
                g_autoit.MouseClick('left')
                g_autoit.Send('aA4+')
##                g_autoit.Send('{DOWN}')
##                g_autoit.Send('{DOWN}')
##                g_autoit.Send('{UP}')
                
                HandleAdobeMsgBox(msgbox_fp)
            elif json_dic['Type'] == '':
                g_autoit.MouseMove(adobe_widget_pos[0], adobe_widget_pos[1])
                g_autoit.MouseClick('left')
                HandleAdobeMsgBox(msgbox_fp)

            page_change_index = int(json_dic['PageChange'])
            if page_change_index > 0:
                for i in range(0, page_change_index):
                    DoAdobePageUp()
                    time.sleep(0.1)
            if page_change_index < 0:
                for i in range(0, abs(page_change_index)):
                    DoAdobePageDown()
                    time.sleep(0.1)
            global EXIT
            if EXIT:
                print('EXIT')
                g_autoit.WinSetOnTop("[CLASS:AcrobatSDIWindow]", "", 0)
                sys.exit()
##            g_autoit.WinSetOnTop("[CLASS:AcrobatSDIWindow]", "", 0)
            return True
        else:
            if time_wait > time_limit:
                return False
            time_wait = time_wait + 1 
            time.sleep(0.1)
            continue
    return True

def CreateMsgBoxLog(logpath):
    fp = codecs.open(os.path.join(logpath, 'msgbox.xml'), 'w', 'utf8')
    fp.write('<xml>')
    return fp

def CloseMsgBoxLog(msglog_fp):
    msglog_fp.write('</xml>\n')
    msglog_fp.close()    


def SaveAdobePageImage(savepath, page_index, page_width, page_height):
    side_width = CalcAdobeSideWidth(page_width)
    side_height = CalcAdobeSideHeight(page_height)
    if side_width == 0:
        x = 0
        y = side_height
        h = page_height
        w = GetSystemMetrics(0)
    else:
        x = side_width
        y = 0
        h = GetSystemMetrics(1)
        w = page_width
        
    png_path = os.path.join(savepath, '%s_Page_%s.png' % (os.path.basename(savepath)[:-4], page_index))
    ImageCatch(png_path, '%s*%s*%s*%s' % (x, y, w, h))

def RunJSAdobe(filepath, save_folder):
    savepath = save_folder + filepath.split(TESTFILE_FOLDER)[1]
    savepath = savepath.replace('#', '_')
    savepath = savepath.replace('&', '_')
    savepath = savepath.replace('{', '_')
    savepath = savepath.replace('}', '_')
    savepath = savepath.replace('%', '_')
    savepath = savepath.replace('+', '_')

    if not os.path.exists(savepath) or os.path.isfile(savepath):
        mkdir(savepath)
    SetJSScript(filepath, savepath)
    
    msg_fp = CreateMsgBoxLog(savepath)

    pos_info_fp = codecs.open('E:\\tem.log', 'r', 'utf8')
    pos_info = pos_info_fp.readlines()
    pos_info_fp.close()

    p = subprocess.Popen(ADOBE_ACROBAT_PATH + ' autotest.pdf')
    time_limit = 100
    time_wait = 0
    while 1:
        time.sleep(0.5)
        print('Do Handle Adobe MsgBox')
        action_type = HandleAdobeMsgBox(msg_fp)
        
        opened_action_type = HandleOtherAction(action_type)
     #   print(action_type)
     #   print(opened_action_type)
        if action_type == 10:
            break
        if opened_action_type == 3: # Password
            break
        if opened_action_type != 2:
            time_wait = time_wait + 1
            
            continue

        HandleAdobeMsgBox(msg_fp)
        
        g_autoit.WinActivate("[CLASS:AcrobatSDIWindow]")
      #  print(g_autoit.WinActivate("[CLASS:AcrobatSDIWindow]")) 
        if g_autoit.WinActive("[CLASS:AcrobatSDIWindow]"):
            global g_adobe_opened
            g_adobe_opened = True

            adobe_page_index = 0
            adobe_page_info = {}
            adobe_page_info[adobe_page_index] = 0 # (pageIndex, pageWidth)

            one_page_end = False
         #   print (one_page_end)
         #   print (pos_info)
            page_index=0
            for js_line in pos_info:
                print(js_line)
                js = json.loads(js_line)
                if js['Type'] == 'Text':
                    continue

##                g_autoit.WinSetOnTop("[CLASS:AcrobatSDIWindow]", "", 1)

                page_size = js['PageSize'].split('*')
                adobe_page_info[adobe_page_index] = page_size
                if page_index != int(js['Index']):
                    SaveAdobePageImage(savepath, adobe_page_index, \
                                    float(adobe_page_info[adobe_page_index][0]),\
                                    int(adobe_page_info[adobe_page_index][1]))
                page_index = int(js['Index'])
                print(page_index)

                if js['Type'] == 'FXQA_STATIC_XFA':
                    if TEST_ONLY_ONE_PAGE:
                        break
                else:                
                    #for i in range(0, (page_index - adobe_page_index)):
                    if 0 < (page_index - adobe_page_index):
                        #SaveAdobePageImage(savepath, adobe_page_index, \
                        #                   float(adobe_page_info[adobe_page_index][0]),\
                        #                   int(adobe_page_info[adobe_page_index][1]))
                        
                        if TEST_ONLY_ONE_PAGE:
                            one_page_end = True
                        #    break
                        adobe_page_index = page_index
                        DoAdobePageDown()
                        
                    if one_page_end:
                        #DoAdobePageDown()
                        break
                                            
                    if DoWidgetAction(js, msg_fp) == False:
                        break

            # Save last page
            if TEST_ONLY_ONE_PAGE == False or page_index == 0:
                SaveAdobePageImage(savepath, adobe_page_index, \
                                           int(adobe_page_info[adobe_page_index][0]),\
                                           int(adobe_page_info[adobe_page_index][1]))
                
            g_autoit.WinSetOnTop("[CLASS:AcrobatSDIWindow]", "", 0)

            print('Widget END......')
            time.sleep(1)
            break
        else:
            if time_wait > time_limit:
                break
            time_wait = time_wait + 1 
            time.sleep(0.5)
            print(time_wait)
            continue
            
    # Kill FXQA.
    p.kill()
    CloseMsgBoxLog(msg_fp)


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
                RunJSAdobe(filepath, save_folder + '\\adobe')
                CompareResult(filepath, save_folder)
##                test
                g_fp_runned.write(filepath)
                g_fp_runned.write('\n')
                g_fp_runned.flush()

                global g_adobe_opened
                g_adobe_opened = False

                status_monitor.stop()
                
        

def main():
  #ClearLogSpace()
  #RunTest_Adobe()
##  RunFXQA(testfile_folder)
#    cmd = 'ImageProcessing -g -m 10*10*200*300 -o F:\\tem.png'
#    os.system(cmd)
#    print(cmd)
    RunTest(TESTFILE_FOLDER)

if __name__ == '__main__':
    hotkey = Hotkey()  
    hotkey.start()
    main()
  
