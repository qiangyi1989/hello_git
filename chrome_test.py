#! /usr/bin/env python3
import sys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
##from selenium.common.exceptions import TimeoutException
##from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
##from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import platform
import os
import time
import tempfile
from PIL import Image
if platform.system() == 'Windows':
    from PIL import ImageGrab
    from FX_Keyboard import *
    import ctypes
    import ctypes.wintypes
    import win32api, win32con
    from FX_WindowsAutomation import *
    g_k = SendKey()
else:
    import pyscreenshot as ImageGrab
    sys.path.append('unix')
    from pymouse import PyMouse
    from pykeyboard import PyKeyboard
    g_k = PyKeyboard()
    g_m = PyMouse()
##


import threading, subprocess
import sys

import json
##import win32com.client
##g_autoit = win32com.client.Dispatch("AutoItX3.Control")

if platform.system() == 'Windows':
    CHROME_SRC_PATH = 'E:/google/windows/src'
    CHROMEDRIVE_PATH = 'E:\\google\\test\\chromedriver_win32/chromedriver.exe'
    CHROME_FOXIT_PATH = 'E:/google\\chromium\\src\\out\\Debug\\chrome.exe'
    ##CHROME_ADOBE_PATH = os.path.join('C:', 'Program Files (x86)', 'Google/Chrome/Application/chrome.exe')#'\"C:/Program Files (x86)/Google/Chrome/Application/chrome.exe\"'
    CHROME_ADOBE_PATH = 'C:\\Users\\Administrator\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe'
    TEST_TESTFILE_PATH = 'E:\\google\\test\\testfiles'
    TEST_LOG_PATH = 'E:/google/test/log'
    TEST_XFAPOSLOG_PATH = 'E:\\google\\test\\XFAPOS'
else:
    CHROME_SRC_PATH = 'E:/google/windows/src'
    CHROMEDRIVE_PATH = '/home/qa/google/test/chromedriver'
    CHROME_FOXIT_PATH = '/home/qa/google/chrome/src/out/Debug/chrome'
    ##CHROME_ADOBE_PATH = os.path.join('C:', 'Program Files (x86)', 'Google/Chrome/Application/chrome.exe')#'\"C:/Program Files (x86)/Google/Chrome/Application/chrome.exe\"'
    CHROME_ADOBE_PATH = 'C:\\Users\\Administrator\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe'
    TEST_TESTFILE_PATH = '/home/qa/google/test/testfiles'
    TEST_LOG_PATH = '/home/qa/google/test/log'
    TEST_XFAPOSLOG_PATH = '/home/qa/google/test/XFAPOS'


TEST_ONLY_ONE_PAGE = True

LABTOP = True
if LABTOP:
    PRINT_BUTTON_POSITION_LIST = [(1478, 23), (1470, 23), (1492, 22)]
##    PRINT_BUTTON_POSITION = (1478, 23)
    FITPAGE_BUTTON_POSITION = (1527, 726)
    API_WARN_POSITION = (1483, 0)
else:
    PRINT_BUTTON_POSITION_LIST = [(1795, 23), (1737, 23), (1812, 23)]]
    FITPAGE_BUTTON_POSITION = (1847, 910)
    API_WARN_POSITION = (1783, 0)

g_err_fp = open('errlog.log', 'a')
g_openfailed_fp = open('openfailed.log', 'a')
##g_runned_fp = open('runlog.log', 'a')
    

def FX_CloseProcess(pid):
    if platform.system() == 'Windows':
        os.popen('taskkill /F /PID %d' % pid)
    else:
        os.kill(pid, 0)

def FX_Exit():
    pid = os.getpid()
    FX_CloseProcess(pid)

def FX_MouseMove(x, y):
    if platform.system() == 'Windows':
        win32api.SetCursorPos((int(x), int(y)))
    else:
        global g_m
        g_m.move(x, y)

def FX_GetScreenWidth():
    if platform.system() == 'Windows':
        return win32api.GetSystemMetrics(0)
    else:
        global g_m
        return g_m.screen_size()[0]

def FX_GetScreenHeight():
    if platform.system() == 'Windows':
        return win32api.GetSystemMetrics(1)
    else:
        global g_m
        return g_m.screen_size()[1]
    
    
class Hotkey(threading.Thread):
    def run(self):  
        global EXIT
        user32 = ctypes.windll.user32
        if not user32.RegisterHotKey(None, 99, win32con.MOD_ALT, win32con.VK_F3):
            raise
        try:  
            msg = ctypes.wintypes.MSG()  
            while user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:  
                if msg.message == win32con.WM_HOTKEY:  
                    if msg.wParam == 99:
                        print('Force Exit.')
                        FX_Exit()
                        return  
                user32.TranslateMessage(ctypes.byref(msg))  
                user32.DispatchMessageA(ctypes.byref(msg))  
        finally:
            user32.UnregisterHotKey(None, 1)
            
def FX_MouseLClick(x, y):
    if platform.system() == 'Windows':
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, int(x), int(y), 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, int(x), int(y), 0, 0)
    else:
        global g_m
        g_m.click(x, y, 1)

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

g_run_time = 0
class CrashDeathMonitor(threading.Thread):
  def __init__(self, browser, filepath, timeout):
    threading.Thread.__init__(self)
    self.browser = browser
    self.filepath = filepath
    self.timeout = timeout
    self.state = True
    if platform.system() == 'Windows':
      self.kill_cmd = 'taskkill -f -im chrome.exe'
    else:
      self.kill_cmd = 'killall chrome'

  def run(self):
    global g_run_time
    global g_autotest_crash_log_fp
    while self.state:
      if g_run_time > self.timeout:
        print('Chrome Crash')
        imager = ImageProcesser(self.filepath)
        image_save_path = os.path.join(IMAGE_FOXIT_SAVE_PATH, os.path.basename(self.filepath)[:-1]+'_crash.png')
        print(('Crash save %s' % image_save_path))
        imager.CatchImage(image_save_path, IMAGE_FOXIT_CATCH_RANGE)
        os.popen(self.kill_cmd)
        os.popen('taskkill -f -im WerFault.exe')
        os.popen('taskkill -f -im chromedriver.exe')
        g_autotest_crash_log_fp.write('%s\n' % self.filepath)
        g_autotest_crash_log_fp.flush()

##        self.browser.close()
##        self.broser.quit()
        g_run_time = 0
        self.state = False
        break
      else:
        time.sleep(1)
        g_run_time += 1
        cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

  def stop(self):
    print('Process Stop ... \n')
    self.state = False
    #qa_listen.g_listen_stop = 1


def GetAsanLog(chromedriver_log_path):
  fp = open(chromedriver_log_path, 'r')
  bufs = fp.read()
  pos_b = bufs.find('ASAN:')
  pos_e = bufs.find('==10==ABORTING')
  fp.seek(pos_b)
  #print(fp.read(pos_e-pos_b))
  asan_log = fp.read(pos_e - pos_b)
  fp.close()
  return asan_log

def ParseAsanLog(log_str, log_path):
  os.chdir(CHROME_SRC_PATH)
  fp = open(os.path.join(tempfile.gettempdir(), 'asantem.log'), 'w')
  fp.write(log_str)
  fp.close()
  os.popen('cat ' + os.path.join(tempfile.gettempdir(), 'asantem.log') + ' | tools/valgrind/asan/asan_symbolize.py | c++filt 2>&1 | tee ' + log_path)


def CheckAlert(browser):
  try:
    alert = browser.switch_to_alert()
    alert.accept()
    print('alert')
  except:
    print('no alert')
    return




def ParseXFALog(log_str):
  info_dic = {}
  info_dic['id'] = log_str[:log_str.find('.')]
  log_str = log_str[log_str.find('.')+1:]
  info_dic['page'] = log_str[:log_str.find('.')]
  log_str = log_str[log_str.find('.[')+1:]
  info_dic['page_size'] = log_str[log_str.find('[') + 1: log_str.find(']')]
  log_str = log_str[log_str.find('.[')+1:]
  info_dic['type'] = log_str[log_str.find('[') + 1: log_str.find(']')]
  log_str = log_str[log_str.find('.[')+1:]
  info_dic['name'] = log_str[log_str.find('[') + 1: log_str.find(']')]
  log_str = log_str[log_str.find('.[')+1:]
  info_dic['page_pos'] = log_str[log_str.find('[') + 1: log_str.find(']')]
  log_str = log_str[log_str.find('.[')+1:]
  info_dic['ui_pos'] = log_str[log_str.find('[') + 1: log_str.find(']')]
  log_str = log_str[log_str.find('.[')+1:]
  info_dic['dev_pos'] = log_str[log_str.find('[') + 1: log_str.find(']')]
  return info_dic

def SeleniumClick(browser, pos_x, pos_y):
  try:
      print(ActionChains(browser).move_by_offset(pos_x, pos_y).click().perform())
      print(('click:%d,%d' % (pos_x, pos_y)))
  except Exception as e:
    print(e)
    if str(e).find('unexpected alert open') != -1:
      image_save_path = os.path.join(IMAGE_FOXIT_SAVE_PATH, imager.GenerateSaveAlertImgName())
      image_save_path = imager.CatchImage(image_save_path, IMAGE_FOXIT_CATCH_RANGE)
      CheckAlert(browser)
      ActionChains(browser).move_by_offset(pos_x, pos_y).click().perform()
    else:
      return -1
  return 0

def SeleniumMove(browser, pos_x, pos_y):
  try:
      print(ActionChains(browser).move_by_offset(pos_x, pos_y).perform())
      print(('move:%d,%d' % (pos_x, pos_y)))
  except Exception as e:
    print(e)
    if str(e).find('unexpected alert open') != -1:
      image_save_path = os.path.join(IMAGE_FOXIT_SAVE_PATH, imager.GenerateSaveAlertImgName())
      image_save_path = imager.CatchImage(image_save_path, IMAGE_FOXIT_CATCH_RANGE)
      CheckAlert(browser)
##      ActionChains(browser).move_by_offset(pos_x, pos_y).perform()
      SeleniumMove(browser, imager, pos_x, pos_y)
    else:
      return -1
  return 0


def WaitPDFOpen(browser, timeout = 100):
    ti = 0
    while ti<timeout:
        ti += 1
        print('============')
        FX_MouseMove(100, 200)
        time.sleep(0.5)
        FX_MouseMove(100, 10)
        time.sleep(0.5)
        #win32api.SetCursorPos((int(1795), int(23)))
        image = ImageGrab.grab()
        for print_button_pos in PRINT_BUTTON_POSITION_LIST:
            print_button_color = image.getpixel(print_button_pos)
            print(print_button_color)
            if print_button_color == (241, 241, 241):
              print('pdf opened')
              return True
    return False

def FitPageSize():
    FX_MouseMove(FITPAGE_BUTTON_POSITION[0], FITPAGE_BUTTON_POSITION[1])
    time.sleep(1)
    FX_MouseLClick(FITPAGE_BUTTON_POSITION[0], FITPAGE_BUTTON_POSITION[1])
    FX_MouseMove(FITPAGE_BUTTON_POSITION[0] - 100, FITPAGE_BUTTON_POSITION[1])
    time.sleep(0.5)
    FX_MouseLClick(FITPAGE_BUTTON_POSITION[0] - 100, FITPAGE_BUTTON_POSITION[1])

def ReFitPageSize():
    for i in range(2):
        FitPageSize()

def CheckAPIKeyWarn():
    image = ImageGrab.grab()
    normal_page_color = image.getpixel(API_WARN_POSITION)
    if normal_page_color != (57, 60, 62) \
       and normal_page_color != (50, 54, 57):
        return True
    return False

def CloseAPIKeyWarn():
    win32api.SetCursorPos((int(1903), int(17)))
    time.sleep(0.5)
    FX_MouseLClick(1903, 17)

def CalcChromeSideWidth(pdf_page_width):
    screen_width = FX_GetScreenWidth()
    side_width = (screen_width - pdf_page_width) / 2
    return side_width

def CalcChromeSideHeight(pdf_page_height):
    screen_height = FX_GetScreenHeight()
    side_height = (screen_height - pdf_page_height) / 2
    return side_height

def DoChromePageDown(browser):
    print('page down')
    global g_k
    g_k.press_key(g_k.page_down_key)
    g_k.release_key(g_k.page_down_key)
    pass

def CalcChromeWidgetPos(widget_type, chrome_side_width, chrome_side_height, pdf_widget_rect):
    if chrome_side_width == 0:
        pos_y = chrome_side_height + pdf_widget_rect.top
        pos_x = pdf_widget_rect.left
    else:
        pos_y = pdf_widget_rect.top
        pos_x = chrome_side_width + pdf_widget_rect.left

    if widget_type == 'CheckButton':
        pos_x = pos_x + 5
        pos_y = pos_y + 5
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

def DoWidgetAction(browser, json_dic, msgbox_fp=None):
    global g_k
    time_limit = 100
    time_wait = 0
    page_size = json_dic['PageSize'].split('*')
    adobe_side_width = int(CalcChromeSideWidth(int(page_size[0])))
    adobe_size_height = int(CalcChromeSideHeight(int(page_size[1])))
    pdf_widget_rect = GetPDFWidgetRect(json_dic['Rect'])
    
    chrome_widget_pos = CalcChromeWidgetPos(json_dic['Type'], adobe_side_width, adobe_size_height, pdf_widget_rect)
    print('Pos: (%d, %d)' % (chrome_widget_pos[0], chrome_widget_pos[1]))
    if json_dic['Type'] == '':
        FX_MouseMove(chrome_widget_pos[0], chrome_widget_pos[1])
        FX_MouseLClick(chrome_widget_pos[0], chrome_widget_pos[1])
    elif json_dic['Type'] == 'Button':
##        return
        print('Button:(%d, %d)' % (chrome_widget_pos[0], chrome_widget_pos[1]))
        FX_MouseMove(chrome_widget_pos[0], chrome_widget_pos[1])
        FX_MouseLClick(chrome_widget_pos[0], chrome_widget_pos[1])
        
##        fff
    elif json_dic['Type'] == 'TextEdit':
##        return
        print('TextEdit:(%d, %d)' % (chrome_widget_pos[0], chrome_widget_pos[1]))
        FX_MouseMove(chrome_widget_pos[0], chrome_widget_pos[1])
        FX_MouseLClick(chrome_widget_pos[0], chrome_widget_pos[1])
        g_k.type_string('abcd1234')
        

    elif json_dic['Type'] == 'CheckButton':
        print('CheckButton:(%d, %d)' % (chrome_widget_pos[0], chrome_widget_pos[1]))
        FX_MouseMove(chrome_widget_pos[0], chrome_widget_pos[1])
        FX_MouseLClick(chrome_widget_pos[0], chrome_widget_pos[1])
    elif json_dic['Type'] == 'ChoiceList':
        FX_MouseMove(chrome_widget_pos[0], chrome_widget_pos[1])
        FX_MouseLClick(chrome_widget_pos[0], chrome_widget_pos[1])
    elif json_dic['Type'] == '':
        FX_MouseMove(chrome_widget_pos[0], chrome_widget_pos[1])
        FX_MouseLClick(chrome_widget_pos[0], chrome_widget_pos[1])
    time.sleep(0.1)
    
    g_k.press_key(g_k.return_key)
    g_k.release_key(g_k.return_key)
    time.sleep(0.1)
    return True

def CheckCrashImage():
    width = FX_GetScreenWidth()
    height = FX_GetScreenHeight()
    image = ImageGrab.grab((int(width/2 -100), int(height/2 -100), int(width/2 +100), int(height/2 +100)))
    tem_name = os.path.join(tempfile.gettempdir() + 'chromestate.png')
    image.save(tem_name)
    for cmp_png in ['ChromeCrash0.png',\
                    'ChromeCrash1.png',\
                    'ChromeCrash2.png']:
        buf = os.popen('ImageProcessing -c "%s" "%s"' % (tem_name, cmp_png)).read()
        print(buf)
        if float(buf) >= 0.9:
            return 1
    time.sleep(2)
    fx_window = FX_Window(None)
    fatal_window = fx_window.FindWindowByName('Fatal error')
##    print(fatal_window)
    if fatal_window != None:
        while 1:
            if fatal_window == None:
                return 2
            g_k.press_key(g_k.return_key)
            g_k.release_key(g_k.return_key)
            time.sleep(0.5)
            fatal_window = fx_window.FindWindowByName('Fatal error')
    return 0

def RunFoxitChromeTest(testfile_path, log_bufs, chrome_argus, chromedriver_log_path):
##  try:
    global g_autotest_log_fp
    os.environ["webdriver.chrome.driver"] = CHROMEDRIVE_PATH
    webdriver.ChromeOptions.binary_location = CHROME_FOXIT_PATH
    webdriver.Chrome.path = CHROME_FOXIT_PATH
    chrome_options = Options()
    chrome_options.add_argument('--kiosk')

    try:
        browser = webdriver.Chrome(CHROMEDRIVE_PATH, \
                                   0, \
                                   chrome_options, \
                                   service_args=["--verbose", "--log-path="+chromedriver_log_path])
    except:
        time.sleep(10)
        browser = webdriver.Chrome(CHROMEDRIVE_PATH, \
                                   0, \
                                   chrome_options, \
                                   service_args=["--verbose", "--log-path="+chromedriver_log_path])

##    browser.set_window_position(0, 0)
##    browser.set_window_size(VIEW_SIZE_X, VIEW_SIZE_Y)

    url_str = 'file://' + testfile_path
    print(url_str)

    browser.get(url_str)
##    browser.maximize_window()
##    time.sleep(20)
    
    if WaitPDFOpen(browser):
      ActionChains(browser).send_keys(Keys.F11).perform()
      FitPageSize()
##      browser.save_screenshot('E:/tem.png')
    else:
      print('Open failed.')
      global g_openfailed_fp
      g_openfailed_fp.write(testfile_path+'\n')
      g_openfailed_fp.flush()

    if platform.system() == 'Windows':
        if CheckCrashImage() > 0:
            print('Crash')
            g_err_fp.write(testfile_path+'\n')
            g_err_fp.flush()
            return
##    if CheckAPIKeyWarn():
##        CloseAPIKeyWarn()

    chrome_page_index = 0
    chrome_page_info = {}
    chrome_page_info[chrome_page_index] = 0
    msg_fp = None

    for js_line in log_bufs:
        try:
            js = json.loads(js_line)
        except:
            if platform.system() == 'Windows':
                if CheckCrashImage():
                    print('Crash')
                    g_err_fp.write(testfile_path+'\n')
                    g_err_fp.flush()
            browser.close()
            browser.quit()
            return
        try:
            if js['Type'] == 'Text':
                continue
        except:
            print('MsgBox')
            continue
        page_size = js['PageSize'].split('*')
        chrome_page_info[chrome_page_index] = page_size
        
        page_index = int(js['Index'])

        if js['Type'] == 'FXQA_STATIC_XFA':
            if TEST_ONLY_ONE_PAGE:
                break
        else:                
            for i in range(0, (page_index - chrome_page_index)):
##                SaveAdobePageImage(savepath, chrome_page_index, \
##                                   float(adobe_page_info[chrome_page_index][0]),\
##                                   int(adobe_page_info[chrome_page_index][1]))
                
                if TEST_ONLY_ONE_PAGE:
                    one_page_end = True
                    if platform.system() == 'Windows':
                        if CheckCrashImage():
                            print('Crash')
                            g_err_fp.write(testfile_path+'\n')
                            g_err_fp.flush()
                    browser.close()
                    browser.quit()
                    return
                
                DoChromePageDown(browser)
                if page_size != chrome_page_info[chrome_page_index]:
                    print('Resize page')
                    ReFitPageSize()
                chrome_page_index = page_index
##                asdfasdf
                                    
            if DoWidgetAction(browser, js, msg_fp) == False:
                break
##        if TEST_ONLY_ONE_PAGE:
##            one_page_end = True
##            break
    if platform.system() == 'Windows':
        if CheckCrashImage() > 0:
            print('Crash')
            g_err_fp.write(testfile_path+'\n')
            g_err_fp.flush()

    browser.close()
    browser.quit()

    return




def RunTest(chrome_argus, chromedriver_log_path):
    runned_files = ''
    fp_runned = ''
    global g_runned_fp

    g_runned_fp = open('runlog.log', 'r')
    runned_files = g_runned_fp.readlines()
    g_runned_fp.close()

    g_runned_fp = open('runlog.log', 'a')

    #os.chdir('/home/qa/google/src')
    for root, dirs, files in os.walk(TEST_XFAPOSLOG_PATH):
        for file_name in files:
            if os.path.splitext(file_name)[1] != '.log':
                print(file_name)
                continue
        
            log_path = os.path.join(root, file_name)
            if platform.system() == 'Windows':
                if log_path.find('\\Google_testfiles\\') != -1:
                    continue
            else:
                if log_path.find('/Google_testfiles/') != -1:
                    continue
            #log_path = '/home/qa/google/test/XFAPOS/XFA_testfiles/XFA_testfiles/xfaDynamic/0008071_svib-burgerluchtvaartnederlands.log'
            #log_path = '/home/qa/google/test/XFAPOS/XFA_testfiles/mantis-Dynamic/0049398_2013 interim application.log
            #log_path = '/home/qa/google/test/XFAPOS/XFA_testfiles/0首批要检查的文档/Layout/mantis-10634-D120-V4_CB.log'
            fp = open(log_path, 'r')
            log_bufs = fp.readlines()
            fp.close()

            testfile_path = log_path.replace(TEST_XFAPOSLOG_PATH, TEST_TESTFILE_PATH)
            testfile_path = testfile_path[:-4] + '.pdf'

            if (testfile_path + '\n') in runned_files:
                continue
            print(testfile_path)

            chromedriver_log_path = TEST_LOG_PATH + '/chromeDriverLog/' + file_name
            print(chromedriver_log_path)

            action_foxit_state = RunFoxitChromeTest(testfile_path, log_bufs, chrome_argus, chromedriver_log_path)
            g_runned_fp.write(testfile_path + '\n')
            g_runned_fp.flush()
            if platform.system() != 'Windows':
                if CheckChromeDriverLog(chromedriver_log_path):
                    global g_err_fp
                    g_err_fp.write(chromedriver_log_path + '\n')
                    g_err_fp.flush()
          
          

##
##      Combine2Image(imager_foxit, imager_adobe)
##
##      if cmp(platform.system(), 'Linux') == 0:
##        log_str = GetAsanLog(chromedriver_log_path)
##        log_path = os.path.join(TEST_LOG_PATH, file_name) + '.txt'
##        ParseAsanLog(log_str, log_path)
##      fp_runned.write(file_name + '\n')
##      fp_runned.flush()
##
##  g_autotest_log_fp.close()
##  g_autotest_crash_log_fp.close()
##  fp_runned.close()

def ClearLogSpace():
  for root, dirs, files in os.walk(TEST_LOG_PATH):
    for filename in files:
      if os.path.splitext(filename)[1] == '.txt':
        os.remove(os.path.join(root, filename))

def CheckChromeDriverLog(logpath):
    fp = open(logpath, 'r')
    bufs = fp.readlines()
    buf_len = len(bufs) - 1
    while 1:
        if buf_len <= 0:
            return False
        line = bufs[buf_len]
        if line.find('Received signal') != -1:
            return True
        if line.find('Done waiting for pending navigations') != -1:
            return False
        if line.find('ERROR: AddressSanitizer') != -1:
            return True
        buf_len = buf_len - 1
        
def main():
##    time.sleep(3)
##    image = ImageGrab.grab()
##    print(PRINT_BUTTON_POSITION)
##    FX_MouseMove(1417,32)
##    time.sleep(1)
##    print_button_color = image.getpixel((1470, 23))
##    print(print_button_color)
##    lkjlj
    #ClearLogSpace()
##    print(win32api.GetSystemMetrics(0))
##    time.sleep(2)
##    image = ImageGrab.grab()
##    print(image.getpixel((1795, 23)))
##    aaaaaaa
    chrome_argus = '--no-sandbox --enable-print-preview --kiosk --user-data-dir=E:\\google\\chrome_data'
    chromedriver_log_path = os.path.join(tempfile.gettempdir(), 'chromeDriver.log')
    print(chromedriver_log_path)
    RunTest(chrome_argus, chromedriver_log_path)


if __name__ == '__main__':
##  time.sleep(3)
##  print IsMsgBoxActive()
##  print os.path.join(tempfile.gettempdir(), 'chromeDriver.log')
##  print IsHaveToolBar()
##  print os.path.join(IMAGE_FOXIT_SAVE_PATH, os.path.basename('E:/google/test/compare_save\0.2013-01-18 Revisiontest._0.png')+'_crash.png')
##    hotkey = Hotkey()  
##    hotkey.start()
    main()
