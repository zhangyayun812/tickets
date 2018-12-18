# coding: utf-8


import re
import requests
from pprint import pprint

url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9035'
# 拉取站台中文与字母对应关系

response = requests.get(url, verify=False)
# 不需要核实打开URL

stations = re.findall(u'([\u4e00-\u9fa5]+)\|([A-Z]+)',response.text)
# 提取URL返回JSON中 简体中文|字母  格式

pprint(dict(stations), indent=4)
# 格式化打印，以空格4为间隔
