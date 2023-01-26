from .data_class import data_cl, Statuses
from .proxy import Proxy_Class
from .captcha import Captcha
from csv_utils import CsvCheck
from config import csv
import multiprocessing
from seleniumwire import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
import seleniumwire.undetected_chromedriver as uc
from dataclasses import dataclass
from colorama import Fore
from loguru import logger as log
import os
import pandas as pd
from time import sleep, time
import random
import traceback
import warnings
import pathlib
ua = UserAgent()
warnings.filterwarnings("ignore")
a_z = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
homeDir = (r'\\').join(os.path.abspath(__file__).split('\\')[:-2])


@dataclass
class Flow:
    data: data_cl
    data_q: multiprocessing.Queue
    proxy: Proxy_Class
    Lock: multiprocessing.Lock
    proxy_list: list
    delay: str
    driver: webdriver.Chrome = None
    wait: WebDriverWait = None
    ip: str = None
    csv: CsvCheck = None
    count_accs: int = None
    count_make_accs: multiprocessing.Value = None
    excel_file: CsvCheck = None

    def start_driver(self, anticaptcha_on=False, anticaptcha_path=None, headless=False, metamask=False, metamask_path=None):

        self.activate_delay()
        self.log_debug_with_lock('СТарт драйвера')
        # self.ads.creade_ads_profile(cookie=self.cookie)
        # self.driver = self.ads.connect_to_ads_selenium(self.ads.start_ads_profile())
        options_c = uc.ChromeOptions()
        # options_c.add_experimental_option(
        #     "prefs", {"profile.default_content_setting_values.notifications": 1})
        # options_c.add_argument(
        #     f'--proxy-server=http://{self.proxy.url_proxy}')
        options_c.add_argument(
            '--disable-blink-features=AutomationControlled')
        options = {'proxy':
                   {'http': f'http://{self.proxy.url_proxy}',
                    'http': f'https://{self.proxy.url_proxy}', }}
        options_c.add_argument(f"user-agent={ua.random}")
        if headless:
            options_c.add_argument("--headless")
        # options_c.add_experimental_option(
        #     'excludeSwitches', ['enable-logging'])
        if anticaptcha_on:
            options_c.add_extension(
                anticaptcha_path)
        if metamask:
            # options_c.add_extension(
            #     metamask_path)
            metamask_path = str(pathlib.Path(metamask_path).absolute())
            options_c.add_argument(f'--load-extension={metamask_path}')
        self.driver = uc.Chrome(
            options=options_c, seleniumwire_options=options, service_log_path='NUL')
        self.driver.set_window_size(1700, 1080)
        self.wait = WebDriverWait(self.driver, 30)
        #self.driver.switch_to.window(self.driver.window_handles[-1])
        if metamask:
            window_name = 'metamask'
            for i in self.driver.window_handles:
                print('check')
                self.driver.switch_to.window(i)
                if window_name in self.driver.title.lower():
                    break

    def activate_delay(self):
        d = self.delay
        if d == '0':
            return ''
        elif '-' in d:
            first, two = map(float, d.split('-'))
            sleep(random.randint(int(round(first*60, 0)), int(round(two*60, 0))))
        else:
            sleep(int(round(float(d)*60, 0)))

    def activate_anti_captcha(self,):
        self.get_new('https://httpbin.org/ip')
        Captcha.activate_anti_captcha(self.driver)

    def get_new(self, link):
        for num, i in enumerate(range(15)):
            try:
                self.driver.get(link)
                return True
            except Exception as e:
                self.log_debug_with_lock(
                    f'{self.data} -- get_new ({link}-- {traceback.format_exc()}')
            if num == 14:
                raise Exception

    def wait_2_elements(self, first_elem, second_elem) -> int:
        self.wait.until(EC.any_of(lambda x: x.find_element(
            By.XPATH, first_elem),
            lambda x: x.find_element(By.XPATH, second_elem)))
        try:
            self.driver.find_element(By.XPATH, first_elem)
            return 1
        except Exception as e:
            return 2

    def click_for_x_y(self, x, y):
        self.actions = ActionChains(self.driver)
        self.actions.move_by_offset(x, y).click().perform()
        self.actions.reset_actions()

    def close_driver(self):
        try:
            self.driver.quit()
        except:
            pass

    def check_frame_and_window(self, frame, frame_elem, window, window_elem, timeout=30):
        time_start = time()
        while time() - time_start < timeout:
            self.driver.switch_to.window(window)
            try:
                self.driver.switch_to.frame(frame)
                self.driver.find_element(By.XPATH, frame_elem)
                return 1
            except Exception as e:
                pass
            self.driver.switch_to.window(window)
            try:
                self.driver.find_element(By.XPATH, window_elem)
                return 2
            except Exception as e:
                pass
        raise

    def wait_3_elements(self, first_elem, second_elem, third_elem) -> int:
        self.wait.until(EC.any_of(lambda x: x.find_element(
            By.XPATH, first_elem),
            lambda x: x.find_element(By.XPATH, second_elem),
            lambda x: x.find_element(By.XPATH, third_elem)))
        try:
            self.driver.find_element(By.XPATH, first_elem)
            return 1
        except Exception as e:
            try:
                self.driver.find_element(By.XPATH, second_elem)
                return 2
            except Exception as e:
                return 3

    def wait_many_elements(self, elems: list[str]):
        lst = []
        self.wait.until(EC.any_of(*[EC.visibility_of_element_located((By.XPATH, elem)) for elem in elems]))
        for num, i in enumerate(elems):
            try:
                self.driver.find_element(By.XPATH, i)
                return num+1
            except:
                pass
        raise

    def wait_and_return_elem(self, xpath, sec=30, sleeps=None):
        self.wait = WebDriverWait(self.driver, sec)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        if sleeps:
            sleep(sleeps)
        return self.driver.find_element(By.XPATH, xpath)

    def wait_click(self, xpath, sleeps=None, sec=30):
        self.wait = WebDriverWait(self.driver, sec)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        if sleeps:
            sleep(sleeps)
        self.driver.find_element(By.XPATH, xpath).click()
        self.wait = WebDriverWait(self.driver, 30)

    def log_debug_with_lock(self, text: str):
        self.Lock.acquire()
        log.debug(text)
        self.Lock.release()

    def wait_send(self, xpath, keys):
        self.wait.until(lambda x: x.find_element(By.XPATH, xpath))
        self.driver.find_element(By.XPATH, xpath).send_keys(keys)

    def log_error(self, desc=None):
        self.log_debug_with_lock(
            f'{self.data} -- {traceback.format_exc()}' + f' -- {desc}' if desc else '')

    def run(self, list_func, attempts=2):
        res = ''
        add_to_end = False
        for func in list_func:
            try:
                res = func()
            except Exception as e:
                res = Statuses.error
                self.log_debug_with_lock(
                    f'{self.data} -- {traceback.format_exc()}')
        if not self._check_valid_thread(res) and res != Statuses.nevalid_ds:
            self.data_q.put(self.data)
            add_to_end = True
        return res, add_to_end

    def _check_valid_thread(self, res):
        if res != Statuses.success:
            return False
        return True

    def zapysk(self, list_func):
        res, add_to_end = self.run(list_func)
        self.count_make_accs.value += 1
        dop_txt = (' -- Перенос в конец очереди' if add_to_end else '')
        txt = f'{self.count_make_accs.value}/{self.count_accs}' + dop_txt
        if not self._check_valid_thread(res):
            print(Fore.RED + txt)
            self.log_debug_with_lock(f'{txt}')
            try:
                self.driver.save_screenshot(
                    f'{homeDir}\\Screenshots_error\\{self.data.ds_token}.png')
            except Exception as e:
                self.log_debug_with_lock(
                    f'{self.data} -- {traceback.format_exc()}')
                pass
        else:
            print(Fore.GREEN + txt)
        self.close_driver()
        self.proxy_list.append(self.proxy)
        _data = {'seed': self.data.seed, 'result': f'{res}{dop_txt}', 'token':self.data.ds_token}
        self.excel_file.add_string(_data)
        if not add_to_end:
            self.csv.add_string({'data': f'{self.data.string}'})

    def authorize_discord(self, att=1):
        ans = self.wait_many_elements([
            '//input[@name="password"]', '//button[@class="button-f2h6uQ lookFilled-yCfaCM colorBrand-I6CyqQ sizeMedium-2bFIHr grow-2sR_-F"]'])
        if ans == 1:
            func = '''function login(token) {
                        setInterval(() => {
                            document.body.appendChild(document.createElement `iframe`).contentWindow.localStorage.token = `"${token}"`
                        }, 50);
                        setTimeout(() => {
                            location.reload();
                        }, 2500);
                        }
                        '''
            self.driver.execute_script(
                func + f"login('{self.data.ds_token}');")
            sleep(10)
            elems = ['//button[@class="button-f2h6uQ lookFilled-yCfaCM colorBrand-I6CyqQ sizeMedium-2bFIHr grow-2sR_-F"]',
                     '//section[@class="panels-3wFtMD"]',
                     '//div[contains(.,"You need to verify your account")]',
                     '//input[@name="password"]']
            ans = self.wait_many_elements(elems)
            if ans == 4:
                if att == 3:
                    return Statuses.nevalid_ds
                self.driver.refresh()
                self.authorize_discord(att=att+1)
            elif ans == 3:
                return Statuses.nevalid_ds
            elif ans == 2:
                return Statuses.need_click_button
            elif ans == 1:
                self.wait_click(
                    '//button[@class="button-f2h6uQ lookFilled-yCfaCM colorBrand-I6CyqQ sizeMedium-2bFIHr grow-2sR_-F"]')
                self.log_debug_with_lock(
                    f'{self.data} -- прожали авториз (дс)')
                return Statuses.success

    def connect_discord(self, xpath=False):
        cur = self.driver.current_window_handle
        counts = len(self.driver.window_handles)
        if xpath:
            self.wait_click(xpath)
        self.wait.until(EC.number_of_windows_to_be(counts+1))
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.wait = WebDriverWait(self.driver,60)
        ans = self.authorize_discord()
        self.wait = WebDriverWait(self.driver,30)
        if ans in [Statuses.nevalid_ds]:
            return ans
        elif ans == Statuses.need_click_button:
            self.driver.close()
            self.wait.until(EC.number_of_windows_to_be(counts))
            self.driver.switch_to.window(cur)
            self.connect_discord(xpath=xpath)
        elif ans == Statuses.success:
            self.wait.until(EC.number_of_windows_to_be(counts))
            self.driver.switch_to.window(cur)
            return Statuses.success

    def restart_metamask(self):
        for i in range(10):
            try:
                self.driver.switch_to.window(self.driver.window_handles[0])
                self.driver.switch_to.new_window('tab')
                break
            except:print(traceback.format_exc())
        self.get_new(
            'chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html#onboarding/welcome')

    def connect_metamask_to_site(self, xpath=False, get=None):
        cur = self.driver.current_window_handle
        counts = len(self.driver.window_handles)
        if xpath:
            self.wait_click(xpath)
        if get:
            self.get_new(get)
        self.wait.until(EC.number_of_windows_to_be(counts+1))
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.wait_click(
            '//button[@class="button btn--rounded btn-primary"]')  # next
        self.wait_click(
            '//button[@data-testid="page-container-footer-next"]')  # connect
        self.wait.until(EC.number_of_windows_to_be(counts))
        self.driver.switch_to.window(cur)

    def sign_message_metamask(self, xpath=None):
        cur = self.driver.current_window_handle
        counts = len(self.driver.window_handles)
        if xpath:
            self.wait_click(xpath)
        self.wait.until(EC.number_of_windows_to_be(counts+1))
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.wait_click(
            '//button[@data-testid="request-signature__sign"]')  # sign
        self.wait.until(EC.number_of_windows_to_be(counts))
        self.driver.switch_to.window(cur)
        return Statuses.success

    def rega_metamask(self):
        while True:
            ans = self.wait_many_elements([
                '//span[@id="critical-error-button"]', '//button[@data-testid="onboarding-import-wallet"]'])
            if ans == 2:
                self.wait_click(
                    '//button[@data-testid="onboarding-import-wallet"]')
                break
            else:
                try:
                    self.wait_click('//span[@id="critical-error-button"]')
                    sleep(2)
                except:
                    traceback.print_exc()
                    continue
                self.restart_metamask()
        self.wait_click('//button[@data-testid="metametrics-i-agree"]')

        seed_new = self.data.seed.split(' ')
        self.wait_and_return_elem(
            '//input[@data-testid="import-srp__srp-word-0"]')
        for i in range(12):
            self.driver.find_element(
                By.XPATH, f'//input[@data-testid="import-srp__srp-word-{i}"]').send_keys(f'{seed_new[i]}')
        self.wait_click('//button[@data-testid="import-srp-confirm"]')
        self.wait_send(
            '//input[@data-testid="create-password-new"]', 'InFiNiTi2022')
        self.wait_send(
            '//input[@data-testid="create-password-confirm"]', 'InFiNiTi2022')
        self.wait_click('//input[@data-testid="create-password-terms"]')
        self.wait_click('//button[@data-testid="create-password-import"]')
        # всё выполнено
        self.wait_click('//button[@data-testid="onboarding-complete-done"]')
        sleep(2)
        self.get_new(
            'chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html#onboarding/unlock')
        self.wait_send(
            '//input[@data-testid="unlock-password"]', 'InFiNiTi2022')
        self.wait_click('//button[@data-testid="unlock-submit"]')
        self.wait_click(
            '//button[@data-testid="onboarding-complete-done"]')  # ПОнятно!
        self.wait_click('//button[@data-testid="pin-extension-next"]')  # Далее
        sleep(1)
        self.wait_click(
            '//button[@data-testid="pin-extension-done"]')  # Выполнено
        self.wait_click('//button[.="Активность"]')
        sleep(1)
        return Statuses.success

