# -*- coding:utf8 -*-
##from selenium import webdriver
##from selenium.webdriver.common.keys import Keys
##from selenium.common.exceptions import TimeoutException
##from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
##from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
##from selenium.webdriver.common.action_chains import ActionChains
##from selenium.webdriver.chrome.options import Options
##import selenium

import os
import time
import tempfile
import codecs
import platform

import threading, subprocess
import sys
import shutil
import signal

if platform.system() == 'Windows':
    import win32com.client
    g_autoit = win32com.client.Dispatch("AutoItX3.Control")

##abs_dir = 'E:\\WORK\\quality_control\\SET\\XFATest\\log\\foxit\\0首批要检查的文档\\foxit脚本执行时间长\\ACCOUNTS.PDF'
##os.mkdir(abs_dir)
##asdf

CHROME_SRC_PATH = 'E:/google/windows/src'
CHROMEDRIVE_PATH = 'E:/google/chromedriver_win32/chromedriver.exe'
CHROME_FOXIT_PATH = 'E:/google\\windows\\src\\out\\Release\\chrome.exe'
##CHROME_ADOBE_PATH = os.path.join('C:', 'Program Files (x86)', 'Google/Chrome/Application/chrome.exe')#'\"C:/Program Files (x86)/Google/Chrome/Application/chrome.exe\"'
CHROME_ADOBE_PATH = 'C:\\Users\\Administrator\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe'

ADOBE_ACROBAT_PATH = '"D:\\Program Files (x86)\\Adobe\\Acrobat 11.0\\Acrobat\\Acrobat.exe"'
FXQA_DEMO_PATH = '/Volumes/1/XX/build-XFATest_Mac-Desktop_Qt_5_5_1_clang_64bit-Debug/XFATest.app/Contents/MacOS/XFATest'

TESTFILE_FOLDER = u'/Volumes/1/XX/google/test'
g_fp_runned = codecs.open('runned.txt', 'a', 'utf8')
g_fp_err = codecs.open('errpdf.txt', 'a', 'utf8')

g_time_id = 0

g_currnt_testfile = ''
g_test_process = ''

g_adobe_opened = True

VIEW_SIZE_X = 1019
VIEW_SIZE_Y = 800
VIEW_BOTTOM_SIZE = 965

ADOBE_PAGECORNER_COLOR = '0x565656'
ADOBE_TOOLBAR_COLOR = '0xcdcdcd'
ADOBE_PAGECORNER_POS = '5,1031'
ADOBE_HIGHLIGHT_BUTTON_0 = '6,163'
ADOBE_HIGHLIGHT_BUTTON_1 = '19,123'

TEST_TESTFILE_PATH = 'E:/google/test/testfiles'
TEST_LOG_PATH = 'log'
TEST_XFAPOSLOG_PATH = 'E:\\google\\test\\XFAPOS'
TEST_XFAPOSLOG_PATH = 'E:\\google\\test\\tem'

IMAGE_FOXIT_CATCH_RANGE = '0*100*1720*850'
IMAGE_ADOBE_CATCH_RANGE = '0*100*1720*850'
IMAGE_FOXIT_SAVE_PATH = 'E:/google/test/foxit_save'
IMAGE_ADOBE_SAVE_PATH = 'E:/google/test/adobe_save'
IMAGE_COMPARE_SAVE_PATH = 'E:/google/test/compare_save'

g_autotest_log = os.path.join(TEST_LOG_PATH, 'qa_autotest.log')
g_autotest_runned_log = os.path.join(TEST_LOG_PATH, 'qa_runned_file.log')
g_autotest_crash_log = os.path.join(TEST_LOG_PATH, 'qa_crash_file.log')
g_autotest_log_fp = ''
g_autotest_crash_log_fp = ''

class StatusMonitor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.is_break = False

    def run(self):
        global g_time_id
        while not self.is_break:
            g_time_id = g_time_id + 1
            time.sleep(1)
            if g_time_id > 1200:
                g_time_id = 0
                g_fp_err.write('LONG TIME:')
                g_fp_err.write(g_currnt_testfile + '\n')
                g_fp_err.flush()
                global g_test_process
                os.popen('pkill XFATest')
                print(g_test_process.pid)
                print('===========================')
                break
                
    def stop(self):
        self.is_break = True

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
        if dir_index >= len(dir_list):
            break
        abs_dir = os.path.join(abs_dir, dir_list[dir_index])
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

##g_run_time = 0
##class CrashDeathMonitor(threading.Thread):
##  def __init__(self, browser, filepath, timeout):
##    threading.Thread.__init__(self)
##    self.browser = browser
##    self.filepath = filepath
##    self.timeout = timeout
##    self.state = True
##    if cmp(platform.system(), 'Windows') == 0:
##      self.kill_cmd = 'taskkill -f -im chrome.exe'
##    else:
##      self.kill_cmd = 'killall chrome'
##      
##  def run(self):
##    global g_run_time
##    global g_autotest_crash_log_fp
##    while self.state:
##      if g_run_time > self.timeout:
##        print('Chrome Crash')
##        imager = ImageProcesser(self.filepath)
##        image_save_path = os.path.join(IMAGE_FOXIT_SAVE_PATH, os.path.basename(self.filepath)[:-1]+'_crash.png')
##        print 'Crash save %s' % image_save_path
##        imager.CatchImage(image_save_path, IMAGE_FOXIT_CATCH_RANGE)
##        os.popen(self.kill_cmd)
##        os.popen('taskkill -f -im WerFault.exe')
##        os.popen('taskkill -f -im chromedriver.exe')
##        g_autotest_crash_log_fp.write('%s\n' % self.filepath)
##        g_autotest_crash_log_fp.flush()
##        
####        self.browser.close()
####        self.broser.quit()
##        g_run_time = 0
##        self.state = False
##        break
##      else:
##        time.sleep(1)
##        g_run_time += 1
##        cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
##              
##  def stop(self):
##    print('Process Stop ... \n')
##    self.state = False
##    #qa_listen.g_listen_stop = 1
##
##class ImageProcesser:
##  def __init__(self, filepath=''):
##    self.filepath = filepath
##    self.action_index = 0
##    self.action_alert_index = 0
##    self.action_image_list = []
##    self.action_alert_image_list = []
##          
##  def GenerateSaveImgName(self, filename, other_str=''):
##    saveImgName = filename[:-4] + other_str + '_' + str(self.action_index) + '.png'
##    self.action_index += 1
##    self.action_image_list.append(saveImgName)
##    return saveImgName
##
##  def GenerateSaveAlertImgName(self, other_str=''):
##    saveImgName = os.path.basename(self.filepath)[:-4] + other_str + '_alert_' + str(self.action_alert_index) + '.png'
##    self.action_alert_index += 1
##    self.action_alert_image_list.append(saveImgName)
##    return saveImgName 
##
##  def CatchImage(self, out_filename, range_catch):
##    cmd = 'ImageProcessing -g ' + '-m ' + range_catch + ' -o ' + '\"' + out_filename + '\"'
##    print cmd
##    os.popen(cmd)
##
##  def CompareImage(self, image0, image1, diff_out_image):
##    cmd = 'ImageProcessing -c ' \
##          + '\"' + image0 + '\"' \
##          + ' \"' + image1 + '\"' \
##          +' -o ' + '\"' + diff_out_image + '\"'
##    os.popen(cmd)
##
##  def CombineImage(self, image0, image1, diff_out_image):
##    cmd = 'ImageProcessing -i ' \
##          + '\"' + image0 + '\"' \
##          + ' \"' + image1 + '\"' \
##          +' -o ' + '\"' + diff_out_image + '\"'
##    os.popen(cmd)
##
##def GetAsanLog(chromedriver_log_path):
##  fp = open(chromedriver_log_path, 'r')
##  bufs = fp.read()
##  pos_b = bufs.find('ASAN:')
##  pos_e = bufs.find('==10==ABORTING')
##  fp.seek(pos_b)
##  #print(fp.read(pos_e-pos_b))
##  asan_log = fp.read(pos_e - pos_b)
##  fp.close()
##  return asan_log
##  
##def ParseAsanLog(log_str, log_path):
##  os.chdir(CHROME_SRC_PATH)
##  fp = open(os.path.join(tempfile.gettempdir(), 'asantem.log'), 'w')
##  fp.write(log_str)
##  fp.close()
##  os.popen('cat ' + os.path.join(tempfile.gettempdir(), 'asantem.log') + ' | tools/valgrind/asan/asan_symbolize.py | c++filt 2>&1 | tee ' + log_path)
##
##  
##def CheckAlert(browser):
##  try:
##    alert = browser.switch_to_alert()
##    alert.accept()
##    print('alert')
##  except:
##    print('no alert')
##    return 
##
##def CheckOpenStatus(browser):
##  log_browser = browser.get_log('browser')
##  if len(log_browser) == 0:
##    return True
##  else:
##    return False
##
##def IsMsgBoxActive():
##  if g_autoit.WinExists('[CLASS:#32770]'):
##    dec_str = '打印'
##    if cmp(g_autoit.WinGetTitle(""), dec_str.decode("GBK")) == 0:
##      return 3
##    dec_str = '发送电子邮件'
##    if cmp(g_autoit.WinGetTitle(""), dec_str.decode("GBK")) == 0:
##      return 2
##    dec_str = 'Adobe Acrobat'
##    if cmp(g_autoit.WinGetTitle(""), dec_str) == 0:
##      return 4
##    dec_str = '警告：JavaScript 窗口 -'
##    if cmp(g_autoit.WinGetTitle(""), dec_str.decode("GBK")) == 0:
##      return 5
##    dec_str = '选择包含表单数据的文件'
##    if cmp(g_autoit.WinGetTitle(""), dec_str.decode("GBK")) == 0:
##      return 6
##    dec_str = '另存为'
##    if cmp(g_autoit.WinGetTitle(""), dec_str.decode("GBK")) == 0:
##      return 7
##    dec_str = '导出表单数据为'
##    if cmp(g_autoit.WinGetTitle(""), dec_str.decode("GBK")) == 0:
##      return 8
##    if g_autoit.WinActive('[CLASS:#32770]'):
##      return 1
##  return 0
##
##def IsHaveToolBar():
##  pos_x = ADOBE_PAGECORNER_POS.split(',')[0]
##  pos_y = ADOBE_PAGECORNER_POS.split(',')[1]
##  page_corner_color = g_autoit.PixelGetColor(pos_x, pos_y)
##  if hex(page_corner_color) == hex(int(ADOBE_PAGECORNER_COLOR,16)):
##    return False
##  return True
##    
##g_havehight_bar = 0
##def AddjustAdobePlugin():
##  if IsHaveToolBar():
##    print 'have tool bar'
##    pos_x = int(ADOBE_HIGHLIGHT_BUTTON_0.split(',')[0])
##    pos_y = int(ADOBE_HIGHLIGHT_BUTTON_0.split(',')[1])
##    highlight_button_color = g_autoit.PixelGetColor(pos_x, pos_y)
##    if hex(highlight_button_color) == hex(int(ADOBE_TOOLBAR_COLOR, 16)):
##      pass
##    else:
##      g_autoit.MouseClick('left', pos_x+15, pos_y, 1)
##      print 'have highlight bar'
##      highlight_button_color = g_autoit.PixelGetColor(pos_x, pos_y)
##      if hex(highlight_button_color) != hex(int(ADOBE_TOOLBAR_COLOR, 16)):
##        global g_havehight_bar
##        g_havehight_bar = 1
##        print 'always have hightlight bar'
##    g_autoit.Send('^h')
##  else:
##    print 'none tool bar'
##    pos_x = ADOBE_HIGHLIGHT_BUTTON_1.split(',')[0]
##    pos_y = ADOBE_HIGHLIGHT_BUTTON_1.split(',')[1]
##    highlight_button_color = g_autoit.PixelGetColor(pos_x, pos_y)
##    if hex(highlight_button_color) == hex(int(ADOBE_PAGECORNER_COLOR, 16)):
##      return False
##    else:
##      print 'have highlight bar'
##      g_autoit.MouseClick('left', pos_x+15, pos_y, 1)
##      if hex(highlight_button_color) != hex(int(ADOBE_TOOLBAR_COLOR, 16)):
##        global g_havehight_bar
##        g_havehight_bar = 1
##        print 'always have hightlight bar'
##      return True
##
##def ParseXFALog(log_str):
##  info_dic = {}
##  info_dic['id'] = log_str[:log_str.find('.')]
##  log_str = log_str[log_str.find('.')+1:] 
##  info_dic['page'] = log_str[:log_str.find('.')]
##  log_str = log_str[log_str.find('.[')+1:]
##  info_dic['page_size'] = log_str[log_str.find('[') + 1: log_str.find(']')]
##  log_str = log_str[log_str.find('.[')+1:]
##  info_dic['type'] = log_str[log_str.find('[') + 1: log_str.find(']')]
##  log_str = log_str[log_str.find('.[')+1:]
##  info_dic['name'] = log_str[log_str.find('[') + 1: log_str.find(']')]
##  log_str = log_str[log_str.find('.[')+1:]
##  info_dic['page_pos'] = log_str[log_str.find('[') + 1: log_str.find(']')]
##  log_str = log_str[log_str.find('.[')+1:]
##  info_dic['ui_pos'] = log_str[log_str.find('[') + 1: log_str.find(']')]
##  log_str = log_str[log_str.find('.[')+1:]
##  info_dic['dev_pos'] = log_str[log_str.find('[') + 1: log_str.find(']')]
##  return info_dic
##
##def SeleniumClick(browser, imager, pos_x, pos_y):
##  try:
##      ActionChains(browser).move_by_offset(pos_x, pos_y).click().perform()
##      print('click:%d,%d' % (pos_x, pos_y))
##  except Exception,e:
##    print e
##    if str(e).find('unexpected alert open') != -1:
##      image_save_path = os.path.join(IMAGE_FOXIT_SAVE_PATH, imager.GenerateSaveAlertImgName())
##      image_save_path = imager.CatchImage(image_save_path, IMAGE_FOXIT_CATCH_RANGE)
##      CheckAlert(browser)
##      ActionChains(browser).move_by_offset(pos_x, pos_y).click().perform()
##    else:
##      return -1
##  return 0
##
##def SeleniumMove(browser, imager, pos_x, pos_y):
##  try:
##      ActionChains(browser).move_by_offset(pos_x, pos_y).perform()
##      print('move:%d,%d' % (pos_x, pos_y))
##  except Exception,e:
##    print e
##    if str(e).find('unexpected alert open') != -1:
##      image_save_path = os.path.join(IMAGE_FOXIT_SAVE_PATH, imager.GenerateSaveAlertImgName())
##      image_save_path = imager.CatchImage(image_save_path, IMAGE_FOXIT_CATCH_RANGE)
##      CheckAlert(browser)
####      ActionChains(browser).move_by_offset(pos_x, pos_y).perform()
##      SeleniumMove(browser, imager, pos_x, pos_y)
##    else:
##      return -1
##  return 0
##
##def AdobeMsgBoxCheck(action_id, imager):
##  global g_printaction_index_L
##  is_msgbox = IsMsgBoxActive()
##  while 1:
##    if is_msgbox == 0:
##      return 0
##    else:
##      print('MsgBox find:%d.' % is_msgbox)
##      image_save_path = os.path.join(IMAGE_ADOBE_SAVE_PATH, imager.GenerateSaveAlertImgName())
##      imager.CatchImage(image_save_path, IMAGE_ADOBE_CATCH_RANGE)
##      print('CatchImage: %s' % image_save_path)
##      if is_msgbox == 4:
##        g_autoit.Send('{ENTER}')
##      elif is_msgbox == 3:
##        g_printaction_index_L.append(action_id)
##        g_autoit.Send('{ESC}')
##      elif is_msgbox == 2:
##        g_autoit.Send('{ESC}')
##      elif is_msgbox == 6:
##        g_autoit.Send('{ESC}')
##      elif is_msgbox == 7:
##        g_autoit.Send('{ENTER}')
##      elif is_msgbox == 8:
##        g_autoit.Send('{ESC}')
##      else:
##        g_autoit.Send('{ENTER}')
##      time.sleep(1)
##      if is_msgbox == 3:
##        g_printaction_index_L.append(action_id)
##      is_msgbox = IsMsgBoxActive()
##  
##g_page_index = 0
##g_printaction_index_L = []
##def TestAction(browser, imager, plugin_type, xfa_widget_info):
##  while 1:
##    try:
##      pdf_embed = browser.find_element_by_name('plugin')
##      break
##    except Exception,e:
##      print e
##      if str(e).find('unexpected alert open') != -1:
##        print '*******'
##        image_save_path = os.path.join(IMAGE_FOXIT_SAVE_PATH, imager.GenerateSaveAlertImgName())
##        image_save_path = imager.CatchImage(image_save_path, IMAGE_FOXIT_CATCH_RANGE)
##        CheckAlert(browser)
##      elif str(e).find('chrome not reachable') != -1:
##        return -1
##      else:
##        print('NOT OPEN PDF EMBED')
##        return -1
##  if cmp(plugin_type, 'ADOBE') == 0:
##    AdobeMsgBoxCheck(-1, imager)
##  action_id = int(xfa_widget_info['id'])
##  pos_dev = xfa_widget_info['dev_pos']
##  pos_y = pos_dev[pos_dev.find(',')+1:]
##  pos_x = pos_dev[:pos_dev.find(',')]
##  try:
##    pos_x = int(pos_x)
##    pos_y = int(pos_y)
##  except:
##    pos_x = 0
##    pos_y = 0
##
##  pos_page = xfa_widget_info['page_pos']
##  widget_w = float(pos_page.split(',')[2])
##  widget_h = float(pos_page.split(',')[3])
##  ui_width = float(xfa_widget_info['ui_pos'].split(',')[2]) + 26
##
##  ELEMENT_TYPE = XFA_ELEMENT_TYPE()
##  widget_type = int(xfa_widget_info['type'])
####  if widget_type == ELEMENT_TYPE.TextEdit:
####    pass
######    pos_x += (widget_w / 2)
######    pos_y += (widget_h / 2)
####  elif widget_type == ELEMENT_TYPE.Text:
####    return 0
##    
##  page_index = int(xfa_widget_info['page'])
##  if page_index > 0:
##    return 0
##  global g_printaction_index
##  if cmp(plugin_type, 'ADOBE') == 0:
##    pos_click_x = pos_x - 10
##    if g_havehight_bar == 0:
##      pos_click_y = pos_y + 10 + 131 - 33
##    else:
##      pos_click_y = pos_y + 10 + 131
##    if pos_click_y > VIEW_BOTTOM_SIZE:
##      print('(%d, %d) out of view, pass.' % (pos_click_x, pos_click_y))
##      return
##    else:
##      print('type %d,(%d, %d)' % (widget_type, pos_click_x, pos_click_y))
##    g_autoit.MouseClick('left', pos_click_x, pos_click_y, 1)
##    time.sleep(0.5)
##    AdobeMsgBoxCheck(action_id, imager)
##
##    widget_type = int(xfa_widget_info['type'])
##    if widget_type == ELEMENT_TYPE.Subform \
##       or widget_type == ELEMENT_TYPE.Button \
##       or widget_type == ELEMENT_TYPE.CheckButton:
##      pass
##    else:
##      g_autoit.Send("FxQA12..,")
##      print('***adobe %d,%d', pos_click_x, pos_click_y)
##      time.sleep(0.2)
##    if widget_type == ELEMENT_TYPE.ChoiceList:
##      pos_dropdown = ui_width + pos_click_x
##      g_autoit.MouseClick('left', pos_dropdown, pos_click_y, 1)
##      g_autoit.MouseClick('left', pos_dropdown, pos_click_y+20, 1)
##
##  # FOXIT TEST
##  else:
##    global g_page_index
##    if page_index != g_page_index:
##      page_down_index = page_index - g_page_index
##      for page_down in range(0, page_down_index):
##        print('GetPageIndex:%d, CurrentPageIndex:%d', (page_index, g_page_index))
##        pdf_embed.send_keys(Keys.ARROW_RIGHT)
##      g_page_index = page_index
##    
##    pos_click_x = pos_x - 13 + 5
##    pos_click_y = pos_y + 5
##    print('(%d, %d)' % (pos_click_x, pos_click_y))
##    ret = SeleniumClick(browser, imager, pos_click_x, pos_click_y)
##    if ret == -1:
##      return -1
##    
##    if widget_type == ELEMENT_TYPE.CheckButton:
##      SeleniumClick(browser, imager, 0, 0)
##      SeleniumClick(browser, imager, 0, 0)
##      
##    print g_printaction_index_L
##    if action_id in g_printaction_index_L:
##      print('***********im print')
##      time.sleep(1)
##      #pdf_embed.send_keys(Keys.ESCAPE)
##      g_autoit.Send('{ESC}')
##      time.sleep(1)
##    
##    if widget_type == ELEMENT_TYPE.Subform \
##       or widget_type == ELEMENT_TYPE.Button \
##       or widget_type == ELEMENT_TYPE.CheckButton:
##      pass
##    else:
##      #pdf_embed.send_keys("FxQA12..,") //slow
##      g_autoit.Send('FxQA12..,')
##      
##    SeleniumMove(browser, imager, -pos_click_x, -pos_click_y)
##    print('move:%d,%d' % (pos_click_x, pos_click_y))
##    if widget_type == ELEMENT_TYPE.ChoiceList:
##      pos_dropdown = ui_width + pos_click_x
##      ret = SeleniumClick(browser, imager, pos_dropdown, pos_click_y)
##      if ret == -1:
##        return -1
##      SeleniumMove(browser, imager, -pos_dropdown, -pos_click_y)
##      ret = SeleniumClick(browser, imager, pos_dropdown, pos_click_y+20)
##      if ret == -1:
##        return -1
##      SeleniumMove(browser, imager, -(pos_dropdown), -(pos_click_y+20))    
##    
##def RunAdobeChromeTest(log_bufs, imager, chrome_argus, chromedriver_log_path):
##  ##  try:
##  os.environ["webdriver.chrome.driver"] = CHROMEDRIVE_PATH
##  webdriver.ChromeOptions.binary_location = CHROME_ADOBE_PATH
##  webdriver.Chrome.path = CHROME_ADOBE_PATH
##  chrome_options = Options()
##  chrome_options.add_argument('--user-data-dir=E:\\google\\chrome_adobe_data')
##  chrome_options.add_argument('--no-sandbox')
##
##  browser = webdriver.Chrome(CHROMEDRIVE_PATH, \
##                             0, \
##                             chrome_options, \
##                             service_args=["--verbose", "--log-path="+chromedriver_log_path])
##
##  browser.set_window_position(0, 0)
##  browser.set_window_size(VIEW_SIZE_X, VIEW_SIZE_Y)
##  testfile_path = log_bufs[0]
##
##  url_str = 'file://' + testfile_path[:-1]
##  url_str = url_str.decode("GBK")
##
##  print url_str
##  browser.get(url_str)
##  browser.maximize_window()
##  
##  print('ADOBE Plugin')
##  time.sleep(4)
##  g_autoit.Send('^y')
##  
##  time.sleep(0.2)
##  g_autoit.Send('87.3')
##  
##  time.sleep(0.5)
##  g_autoit.Send('{ENTER}')
##
##  global g_havehight_bar
##  g_havehight_bar = 0
##  AddjustAdobePlugin()
##  
##  for log_str in log_bufs[1:]:
##    xfa_widget_info = ParseXFALog(log_str)
##    print TestAction(browser, imager, 'ADOBE', xfa_widget_info)
##    
##  image_savepath = os.path.join(IMAGE_ADOBE_SAVE_PATH, imager.GenerateSaveImgName(os.path.basename(log_bufs[0])))
##  imager.CatchImage(image_savepath, IMAGE_ADOBE_CATCH_RANGE)
##
##  try:
##    browser.close()
##    browser.quit()
##  except:
##    os.popen('taskkill -f -im chrome.exe')
##    os.popen('taskkill -f -im WerFault.exe')
##    os.popen('taskkill -f -im chromedriver.exe')
##
##  return (imager.action_index, imager.action_alert_index)
##
##      
##def RunFoxitChromeTest(log_bufs, imager, chrome_argus, chromedriver_log_path):
####  try:
##    global g_autotest_log_fp
##    os.environ["webdriver.chrome.driver"] = CHROMEDRIVE_PATH
##    webdriver.ChromeOptions.binary_location = CHROME_FOXIT_PATH
##    webdriver.Chrome.path = CHROME_FOXIT_PATH
##    chrome_options = Options()
##    chrome_options.add_argument('--no-sandbox')
##
##    browser = webdriver.Chrome(CHROMEDRIVE_PATH, \
##                               0, \
##                               chrome_options, \
##                               service_args=["--verbose", "--log-path="+chromedriver_log_path])
##
##    browser.set_window_position(0, 0)
##    browser.set_window_size(VIEW_SIZE_X, VIEW_SIZE_Y)
##    testfile_path = log_bufs[0]
##    
##    url_str = 'file://' + testfile_path[:-1]
##    url_str = url_str.decode("GBK")
##    print url_str
##    
##    browser.get(url_str)
##    browser.maximize_window()
##    
####    browser.save_screenshot('E:/testsetsetse1.png')
##    g_autotest_log_fp.write('%s\n' % testfile_path)
##    monitor = CrashDeathMonitor(browser, testfile_path, 30)
##    monitor.start()
##
##    single_action_test_state = 0
##    for log_str in log_bufs[1:]:
####      print log_str
##      xfa_widget_info = ParseXFALog(log_str)
##      single_action_test_state = TestAction(browser, imager, 'FOXIT', xfa_widget_info)
####      time.sleep(0.2)
##      if single_action_test_state == -1:
##        g_autotest_log_fp.write('%s.[%s].CRASH' % (testfile_path, log_str ))
##        g_autotest_log_fp.flush()
##        break
##    monitor.stop()
##    global g_run_time
##    g_run_time = 0
##
##    global g_printaction_index_L
##    g_printaction_index_L = []
##    
##    image_savepath = os.path.join(IMAGE_FOXIT_SAVE_PATH, imager.GenerateSaveImgName(os.path.basename(log_bufs[0])))
##    imager.CatchImage(image_savepath, IMAGE_FOXIT_CATCH_RANGE)   
##      
####    if CheckOpenStatus(browser) == False:
####      g_autotest_log_fp.write(testfile_path + ' ------ LOAD ERROR\n')
####      print(testfile_path + ' ------ LOAD ERROR\n')
####      g_autotest_log_fp.flush()
####      browser.quit()
####      return False
####    time.sleep(4)
####    TestAction(browser)
####    
####    #browser.save_screenshot('E:/testsetsetse.png')
####    global g_autotest_log_fp
######    browser.close()
####    run_state = True
####    g_autotest_log_fp.write(testfile_path + ' ------ OK\n')
######  except:
####    run_state = False
####    g_autotest_log_fp.write(testfile_path + ' ------ ERROR\n')
####    print(testfile_path + ' ------ ERROR\n')
##    
####  g_autotest_log_fp.flush()
##    if single_action_test_state != -1:
##      browser.close()
##      browser.quit()
##    
##    return (imager.action_index, imager.action_alert_index)
##  
##def Combine2Image(imager_foxit, imager_adobe):
##  global g_autotest_log_fp
##  cmp_action_count = 0
##  cmp_action_alert_count = 0
##  if len(imager_foxit.action_image_list) < len(imager_adobe.action_image_list):
##    print('***ACTION ERROR***')
##    g_autotest_log_fp.write('ACTION ERROR:(%d, %d)' \
##                            % (len(imager_foxit.action_image_list), len(imager_adobe.action_image_list)))
##    cmp_action_count = len(imager_foxit.action_image_list)
##  elif len(imager_foxit.action_image_list) > len(imager_adobe.action_image_list):
##    print('***ACTION ERROR***')
##    g_autotest_log_fp.write('ACTION ERROR:(%d, %d)' % (len(imager_foxit.action_image_list), \
##                                                       len(imager_adobe.action_image_list)))
##    cmp_action_count = len(imager_adobe.action_image_list)
##  else:
##    cmp_action_count = len(imager_adobe.action_image_list)
##    
##  if len(imager_foxit.action_alert_image_list) < len(imager_adobe.action_alert_image_list):
##    print('***ALERT ACTION ERROR***')
##    g_autotest_log_fp.write('ALERT ACTION ERROR:(%d, %d)' \
##                            %(len(imager_foxit.action_alert_image_list), len(imager_adobe.action_alert_image_list)))
##    cmp_action_alert_count = len(imager_foxit.action_alert_image_list)
##  elif len(imager_foxit.action_alert_image_list) < len(imager_adobe.action_alert_image_list):
##    print('***ALERT ACTION ERROR***')
##    g_autotest_log_fp.write('ALERT ACTION ERROR:(%d, %d)' \
##                            %(len(imager_foxit.action_alert_image_list), len(imager_adobe.action_alert_image_list)))
##    cmp_action_alert_count = len(imager_adobe.action_alert_image_list)
##  else:
##    cmp_action_alert_count = len(imager_adobe.action_alert_image_list)
##
##  print(cmp_action_count, cmp_action_alert_count)
##  for i in range(0, cmp_action_count):
##    save_path = os.path.join(IMAGE_COMPARE_SAVE_PATH, imager_foxit.action_image_list[i])
##    imager_foxit.CombineImage(os.path.join(IMAGE_FOXIT_SAVE_PATH, imager_foxit.action_image_list[i]), \
##                              os.path.join(IMAGE_ADOBE_SAVE_PATH, imager_adobe.action_image_list[i]), \
##                              save_path)
##    
##    print('CompareSave: %s' % save_path)
##
##  for i in range(0, cmp_action_alert_count):
##    save_path = os.path.join(IMAGE_COMPARE_SAVE_PATH, imager_foxit.action_alert_image_list[i])
##    imager_foxit.CombineImage(os.path.join(IMAGE_FOXIT_SAVE_PATH, imager_foxit.action_alert_image_list[i]), \
##                              os.path.join(IMAGE_ADOBE_SAVE_PATH, imager_adobe.action_alert_image_list[i]), \
##                              save_path)
##    print('CompareSave: %s' % save_path)
##
##    
##def RunTest(chrome_argus, chromedriver_log_path):
##  global g_autotest_log_fp
##  g_autotest_log_fp = open(g_autotest_log, 'a')
##  global g_autotest_crash_log_fp
##  g_autotest_crash_log_fp = open(g_autotest_crash_log, 'a')
##
##  runned_files = ''
##  fp_runned = ''
##  if os.path.exists(g_autotest_runned_log):
##    fp_runned = open(g_autotest_runned_log, 'r')
##    runned_files = fp_runned.readlines()
##    fp_runned.close()
##  fp_runned = open(g_autotest_runned_log, 'a')
##  
##  #os.chdir('/home/qa/google/src')
##  for root, dirs, files in os.walk(TEST_XFAPOSLOG_PATH):
##    for file_name in files:
##      if cmp(os.path.splitext(file_name)[1], '.txt') != 0:
##        print file_name
##        continue
####      if (file_name + '\n') in runned_files:
####        print file_name
####        continue
##      xfalog_path = os.path.join(root, file_name)
##      fp = open(xfalog_path, 'r')
##      log_bufs = fp.readlines()
##      fp.close()
##      
##      print 'ready run.'
##      
##      imager_adobe = ImageProcesser(log_bufs[0])
##      action_adobe_state = RunAdobeChromeTest(log_bufs, imager_adobe, chrome_argus, chromedriver_log_path)
##
####      imager_foxit = ImageProcesser(log_bufs[0])
####      action_foxit_state = RunFoxitChromeTest(log_bufs, imager_foxit, chrome_argus, chromedriver_log_path)
####      
####      Combine2Image(imager_foxit, imager_adobe)
####      
####      if cmp(platform.system(), 'Linux') == 0:
####        log_str = GetAsanLog(chromedriver_log_path)
####        log_path = os.path.join(TEST_LOG_PATH, file_name) + '.txt'
####        ParseAsanLog(log_str, log_path)
####      fp_runned.write(file_name + '\n')
####      fp_runned.flush()
####      
####  g_autotest_log_fp.close()
####  g_autotest_crash_log_fp.close()
####  fp_runned.close()

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

def HandleAdobeMsgBox():
  if ContainStr('already exists. Do you want to overwrite it', 'Adobe Acrobat'):
    if FoucsControl('Button1', 'Adobe Acrobat'):
      g_autoit.Send('{SPACE}')
      g_autoit.Send('{ENTER}')
      return 0
  if ContainStr('file already exists', 'Save As'):
    if FoucsControl('Button1', 'Save As'):
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

  if ContainStr('must be prepared for reading', 'Reading Untagged Document'):
      g_autoit.Send('{ESC}')
      return 0
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
  if g_autoit.WinExists("JavaScript Debugger"):
      print('Java Debugger')
      if ContainStr('NotAllowedError', "JavaScript Debugger"):
          g_autoit.WinSetOnTop("JavaScript Debugger", "", 1)
          g_autoit.Send('!{F4}')
          g_autoit.WinSetOnTop("JavaScript Debugger", "", 0)
          return 10 # JS Error, ATTest END.
      else:
          g_autoit.WinSetOnTop("JavaScript Debugger", "", 1)
          g_autoit.Send('!{F4}')
          g_autoit.WinSetOnTop("JavaScript Debugger", "", 0)
          if g_autoit.WinActive("autotest.pdf - Adobe Acrobat Pro"):
              return 10 # Test doc already close.
          return 0
  if g_autoit.WinActive("Warning: JavaScript Window - "):
      g_autoit.Send('{ENTER}')
      return 0
  
  if ContainStr('FXQAAT END', 'Adobe Acrobat'):
      g_autoit.Send('{ENTER}')
      print('EEEEEEENNNNNNNNNDDDDDDDDDD')
      return 10 # ATTest END.
  if g_autoit.WinActive("Adobe Acrobat"):
      g_autoit.OPT("WinDetectHiddenText", 1)
      winText = g_autoit.WinGetText('Adobe Acrobat', '')
      g_autoit.OPT("WinDetectHiddenText", 0)
      winText = ''.join(winText)
      if winText.find('APPCRASH') != -1:
          g_autoit.Send('{ENTER}')
          return 10 # Adobe Crash.
        
  if g_autoit.WinActive("Adobe Acrobat"):
      g_autoit.Send('{ENTER}')
      return 0
  if not g_autoit.WinExists('[CLASS:AcrobatSDIWindow]'):
      global g_adobe_opened
      if g_adobe_opened:
          return 10 # Adobe already exit.
  return 0

def HandleOtherAction(action_id = -1):
    if action_id == 1:
        os.popen('taskkill /IM FireFox.exe /F')
        os.popen('taskkill /IM chrome.exe /F')
        os.popen('taskkill /IM "Internet Explorer.exe" /F')
        return
    os.popen('taskkill /IM FireFox.exe /F')
    os.popen('taskkill /IM chrome.exe /F')
    os.popen('taskkill /IM "Internet Explorer.exe" /F')
      
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
##  print(filepath.split(TESTFILE_FOLDER))
  savepath = save_folder + filepath.split(TESTFILE_FOLDER)[1]
  savepath = savepath.replace('#', '_')
  savepath = savepath.replace('&', '_')
  savepath = savepath.replace('{', '_')
  savepath = savepath.replace('}', '_')
  savepath = savepath.replace('%', '_')
  savepath = savepath.replace('+', '_')
##  print(savepath)
  if not os.path.exists(savepath) or os.path.isfile(savepath):
    mkdir(savepath)
    
  param = ' -f "%s" -s "%s"' % (filepath, savepath)
  cmd = FXQA_DEMO_PATH + ' ' + param
  print(cmd.encode('utf8'))
  p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  global g_test_process
  g_test_process = p
  last_line = ''
  for line in iter(p.stdout.readline, b''):
    print(line)
    last_line = line
    if line.find('Save End') != -1:
      p.kill()
    elif line.find('Crash ERROR') != -1:
      print(line)
      g_fp_err.write(line.decode('utf8').split('ERROR:')[1])
      g_fp_err.write('\n')
      g_fp_err.flush()
    elif line.find('NOT XFA') != -1:
      p.kill()
      return True

  if last_line.find('Save End') == -1 \
    and last_line.find('Crash ERROR') == -1 \
    and last_line.find('NOT XFA') == -1:
        g_fp_err.write('OtherError:')
        g_fp_err.write(g_currnt_testfile)
        g_fp_err.write('\n')
        g_fp_err.flush()
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
##    print(files)
    for filename in files:
      adobe_pngpath = os.path.join(root, filename)
      foxit_pngpath = foxit_savepath + '\\' + filename
##      print(adobe_pngpath)
##      print(foxit_pngpath)
      if not os.path.exists(foxit_pngpath):
        g_fp_err.write(filepath)
        g_fp_err.write('\n')
        g_fp_err.flush()
        print('Error Not Found: %s' % foxit_pngpath)
        break
      compare_save_path = savepath + '/' + filename
      CreateComparePNG(adobe_pngpath, foxit_pngpath, compare_save_path)   
##      print(adobe_pngpath)
##      print(foxit_pngpath)

def SetJSScript(filepath, save_folder):
    js = '''
FXAT_SavePNG = app.trustedFunction( function ()
{

app.beginPriv(); // Explicitly raise privilege
var testDoc = app.openDoc("/%s");
testDoc.saveAs("/%s.png", "com.adobe.acrobat.png");
app.alert("FXQAAT END.");
testDoc.closeDoc();
app.endPriv();
// Additional code may appear below.
});'''

    fp = codecs.open('D:\\Program Files (x86)\\Adobe\\Acrobat 11.0\\Acrobat\\Javascripts\\a.js', 'w')
    
    js_filepath = filepath.replace(':\\', '/').replace('\\', '/')
    js_savepath = (save_folder + '\\' + os.path.basename(filepath)).replace(':\\', '/').replace('\\', '/')[:-4]   

    try:
        fp.write(js % (js_filepath, js_savepath))
    except:        
        tem = str.encode(filepath)
##        print(js_filepath.encode('utf8'))
        js_filepath = js_filepath.encode('utf8')
        js_savepath = js_savepath.encode('utf8')
        
##        print(js_filepath.decode("gb18030", 'ignore'))
        js_filepath = js_filepath.decode("ascii", 'ignore')
        js_savepath = js_savepath.decode("ascii", 'ignore')
        fp.write(js % (js_filepath, js_savepath))

        try:
            shutil.copy(filepath, os.path.join(os.path.dirname(filepath), os.path.basename(js_savepath))+'.pdf')
        except:
            pass
    fp.close()

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

    p = subprocess.Popen(ADOBE_ACROBAT_PATH + ' autotest.pdf')
    while 1:
        time.sleep(0.5)
        print('Do Handle Adobe MsgBox')
        action_type = HandleAdobeMsgBox()
        HandleOtherAction(action_type)
        if (action_type == 10):
            break

        if g_autoit.WinActive("[CLASS:AcrobatSDIWindow]"):
            global g_adobe_opened
            g_adobe_opened = True
            g_autoit.WinSetOnTop("[CLASS:AcrobatSDIWindow]", "", 1)
            time.sleep(0.5)
            HandleOtherAction()

            g_autoit.WinActive("[CLASS:AcrobatSDIWindow]")
            time.sleep(0.5)
            g_autoit.WinSetOnTop("[CLASS:AcrobatSDIWindow]", "", 0)

            if ContainStr('FXQAAT END', 'Adobe Acrobat'):
              g_autoit.Send('{ENTER}')
            ##          asdf
              p.kill()
              break
            time.sleep(1)
##  asdf
    p.kill()

def RunTest(testfile_folder, save_folder):
    fp_runned = codecs.open('runned.txt', 'r', 'utf8')
    runned_list = fp_runned.readlines()
    for root, dirs, files in os.walk(testfile_folder):
        for filename in files:
            sufix = os.path.splitext(filename)[1][1:]
            if sufix.upper() != 'PDF':
                continue
            filepath = os.path.join(root, filename)
            if filepath + '\n' in runned_list:
                continue
            #print(filepath)
            global g_currnt_testfile
            g_currnt_testfile = filepath

            global g_time_id
            g_time_id = 0

            status_monitor = StatusMonitor()
            status_monitor.start()

            if RunFXQA(filepath, save_folder + '/foxit'):
                #RunAdobe(filepath, save_folder + '\\adobe')
##                RunJSAdobe(filepath, save_folder + '\\adobe')
##                CompareResult(filepath, save_folder)
##                sdfsdf
                g_fp_runned.write(filepath)
                g_fp_runned.write('\n')
                g_fp_runned.flush()

                global g_adobe_opened
                g_adobe_opened = False
                status_monitor.stop()
                g_time_id = 0
        
  
def main():
  ClearLogSpace()
##  chrome_argus = '--no-sandbox --enable-print-preview --user-data-dir=E:\\google\\chrome_data'
##  chromedriver_log_path = os.path.join(tempfile.gettempdir(), 'chromeDriver.log')
##  RunTest(chrome_argus, chromedriver_log_path)

  #RunTest_Adobe()
  save_folder = '/Volumes/1/XX/XFATest/log'
##  RunFXQA(testfile_folder)
  RunTest(TESTFILE_FOLDER, save_folder)

if __name__ == '__main__':
  main()
##    fp = codecs.open('errrerun.txt', 'r', 'utf8')
##    buflines = fp.readlines()
##    for line in buflines:
##        if len(line) < 5:
##            continue
##        print(line)
##        testfile = line[:-2]
##        RunFXQA(testfile, 'E:\\WORK\\quality_control\\SET\\XFATest\\log\\temfoixt')
  
##    time.sleep(3)
##    g_autoit.OPT("WinDetectHiddenText", 1)
##    winText = g_autoit.WinGetText('Adobe Acrobat', '')
##    winText = ''.join(winText)
##    print(winText.find('APPCRASH'))
