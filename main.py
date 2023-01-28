from Selen_utils import data_cl, Proxy_Class, Captcha, Flow, Statuses
from csv_utils import Execute, CsvCheck
import config as cf
import multiprocessing
from loguru import logger as log
import imaplib
import queue
from seleniumwire import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import ElementClickInterceptedException
from dataclasses import dataclass
import traceback
import os
import pandas as pd
from time import sleep, time
import random
import warnings
ua = UserAgent()
warnings.filterwarnings("ignore")
a_z = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
homeDir = (r'\\').join(os.path.abspath(__file__).split('\\')[:-1])

datas = cf.datas
csv = cf.csv


class Wifoo(Flow):

    def restart_driver(self):
        self.log_debug_with_lock(f'{self.data} -- restart_driver')
        self.close_driver()
        metamask_path = f'{homeDir}\\files\\metamask.crx'#f'{homeDir}\\files\\nkbihfbeogaeaoehlefnkodbefgpgknn\\10.24.1_0'
        self.start_driver(
            metamask=True, metamask_path=metamask_path, ads=True)
        self.rega_metamask()

    def go(self,):
        if self.proxy.proxy_link:
            self.proxy.change_ip()

        self.log_debug_with_lock(f'Старт потока {self.data}')
        self.restart_driver()
        self.get_new('https://guild.xyz/woofi')
        self.wait_click('//button[@data-dd-action-name="Join"]')#join to guild roles
        self.wait_click('//button[@data-dd-action-name="Connect wallet (JoinModal)"]')# connect wallet
        self.connect_metamask_to_site(xpath='//button[.="MetaMask"]')
        self.sign_message_metamask(xpath='//button[@class="chakra-button css-x1klbh"]')#Verify account
        sleep(3)
        ans = self.connect_discord(xpath='//button[@data-dd-action-name="Connect Discord (JoinModal)"]')
        if ans != Statuses.success:
            return ans
        sleep(3)
        self.wait_click('//button[@class="chakra-button css-lcnqgc"]')#join guild
        sleep(5)
        return Statuses.success

    def start(self,):
        self.zapysk([self.go])


if __name__ == '__main__':
    proxy_q = queue.Queue()
    m = multiprocessing.Manager()
    Logs_to_excel = m.list()
    counter = multiprocessing.Value('i', 0)
    proxy_list = m.list()
    excel_file = CsvCheck(name_file=rf'{homeDir}\\result.xlsx', colums_check=[
                          'seed', 'token', 'result'], type_file='excel')
    excel_file.check_file()
    data_q = datas.get_queue()
    with open(f'{homeDir}\\txt\\proxy.txt') as file:
        for i in file.read().split('\n'):
            prox = Proxy_Class(i)
            proxy_list.append(prox)
    with open(f'{homeDir}\\stop.txt', 'w') as file:
        pass
    Lock = multiprocessing.Lock()
    print(f'Кол-во данных - {datas.count_args}')
    threads_count = int(input(f"Сколько потоков требуется (Прокси указано - {len(proxy_list)})? - "))
    delay = input('Задержка(либо 1-2, либо 0) - ')
    flow = 0
    while True:
        while (not data_q.empty()):
            while len(multiprocessing.active_children())-1 >= threads_count:
                sleep(1)
            for i in range(threads_count-len(multiprocessing.active_children())+1):
                if (not data_q.empty()) and len(proxy_list) > 0:
                    with open(f'{homeDir}\\stop.txt', 'r') as file:
                        if 'true' in file.read():
                            continue
                    data = data_q.get()
                    proxx = random.choice(proxy_list)
                    # proxx.change_ip()
                    proxy_list.remove(proxx)
                    t = multiprocessing.Process(
                        target=Wifoo(data, data_q, proxx, Lock, proxy_list, delay, csv=csv, count_accs=datas.count_args, count_make_accs=counter, excel_file=excel_file).start)
                    t.start()
                    flow += 1
        while len(multiprocessing.active_children()) != 1:
            sleep(1)
        break
