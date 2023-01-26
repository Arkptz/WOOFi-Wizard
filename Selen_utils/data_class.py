from dataclasses import dataclass
from loguru import logger
import sys
import base64


@dataclass
class data_cl:
    string:str
    seed:str=None
    ds_token:str=None
    def __init__(self, string:str) -> None:
        self.string = string
        spl_string = string.split('|')
        ln = len(spl_string)
        if ln == 2 :
            self.seed, self.ds_token = spl_string
        else:
            print(f'Ошибка ввода данных: {string}')
            sys.exit()


class Statuses:
    error = 'Error'
    success = 'Success'
    nevalid = 'Невалид'
    left_captcha = 'Левая капча'
    nevalid_ds = 'Невалид дс'
    need_click_button = 'click_connect'