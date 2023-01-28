import requests
import multiprocessing
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
from Selen_utils import Proxy_Class
from loguru import logger
import config as cfg


class Ads:
    def __init__(self, proxy: Proxy_Class = None, lock: multiprocessing.Lock = None) -> None:
        self.proxy = proxy
        self.url_ads = cfg.url_ads
        self.Lock = lock
        self.group_id = self.get_group_id()

    def get_group_id(self):
        group_id = 0
        resp = ''
        self.Lock.acquire()
        for i in range(25):
            try:
                resp = requests.get(
                    self.url_ads + '/api/v1/group/list', params={'page_size': 100}).json()
                if resp['code'] == 0:
                    resp = resp['data']['list']
                    break
                sleep(1)
            except:
                sleep(2)
        self.Lock.release()
        for i in resp:
            if i['group_name'] == cfg.name_group_ads:
                group_id = i['group_id']
                break
        if group_id == 0:
            print(logger.error(
                f'Отсутствует группа профилей с названием {cfg.name_group_ads}'))
            raise
        return group_id

    def creade_ads_profile(self, cookie=None):
        proxy = self.proxy
        if proxy:
            user_proxy_config = {'proxy_soft': 'other', 'proxy_type': 'http', 'proxy_host': proxy.ip,
                                 'proxy_port': proxy.port, 'proxy_user': proxy.login, 'proxy_password': proxy.password}
        else:
            user_proxy_config = {}
        fingerprint_config = {'location': 'ask', 'canvas': 1, 'webgl_image': 1, 'webgl': 1, 'audio': 1, 'scan_port_type': 1, 'media_devices': 1, 'client_rects': 1,
                              'device_name_switch': 1, 'webrtc': 'proxy', 'speech_switch': 1, 'mac_address_config': {"model": "1", "address": ""}}
        cfg = {'group_id': self.group_id, 'user_proxy_config': user_proxy_config,
               'fingerprint_config': fingerprint_config}
        if cookie and cookie != '':
            cfg['cookie'] = cookie
        # print(cookie)
        open_url = self.url_ads + '/api/v1/user/create'
        self.Lock.acquire()
        for i in range(25):
            try:
                resp = requests.post(open_url, json=cfg).json()
            except:
                continue
            if resp['code'] == 0:
                break
            sleep(1)
        if resp["code"] != 0:
            print(resp["msg"])
            print("please check ads_id")
            self.Lock.release()
            raise
        self.Lock.release()
        self.ads_id = resp['data']['id']
        return resp['data']['id']

    def close_browser(self):
        open_url = self.url_ads + "/api/v1/browser/stop"
        self.Lock.acquire()
        sleep(1)
        resp = ''
        for i in range(25):
            try:
                resp = requests.get(
                    open_url, params={'user_id': [self.ads_id]}).json()
            except:
                continue
            if resp['code'] == 0:
                break
            sleep(1)
        if resp["code"] != 0:
            print(resp["msg"])
            print("please check ads_id")
            self.Lock.release()
            raise
        self.Lock.release()
        sleep(3)

    def del_ads_id(self):
        open_url = self.url_ads + "/api/v1/user/delete"
        self.Lock.acquire()
        sleep(1)
        resp = ''
        for i in range(25):
            try:
                resp = requests.post(
                    open_url, json={'user_ids': [self.ads_id]}).json()
            except:
                continue
            if resp['code'] == 0:
                break
            sleep(1)
        if resp["code"] != 0:
            print(resp["msg"])
            print("please check ads_id")
            self.Lock.release()
            raise
        self.Lock.release()

    def start_ads_profile(self):
        open_url = self.url_ads + "/api/v1/browser/start?user_id=" + self.ads_id
        self.Lock.acquire()
        sleep(1)
        resp = ''
        for i in range(25):
            try:
                resp = requests.get(open_url).json()
            except:
                continue
            if resp['code'] == 0:
                break
            sleep(1)
        if resp["code"] != 0:
            print(resp["msg"])
            print("please check ads_id")
            self.Lock.release()
            raise
        self.Lock.release()
        return resp

    def connect_to_ads_selenium(self, resp):
        chrome_driver = resp["data"]["webdriver"]
        chrome_options = Options()
        chrome_options.add_experimental_option(
            "debuggerAddress", resp["data"]["ws"]["selenium"])
        try:
            driver = webdriver.Chrome(chrome_driver, options=chrome_options)
        except:
            driver = webdriver.Chrome(chrome_driver, options=chrome_options)
        sleep(5)
        # for i in range(10):
        #     try:
        #         driver.switch_to.new_window('tab')
        #         break
        #     except:pass
        return driver
