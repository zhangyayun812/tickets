# coding: utf-8

"""火车票查看器

Usage:
    tickets [-cgdtkz] <from> <to> <date>

Options:
    -h,--help   显示菜单
    -g          高铁
    -d          动车
    -t          特快
    -k          快速
    -z          直达
    -c          动车组

Example:
    tickets 北京 上海 2016-10-10
    tickets -dg 成都 南方 2016-10-10

"""

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
import json
import sys
from docopt import docopt
from stations import stations
from prettytable import PrettyTable
from colorama import init, Fore


class TrainsCollection:
    header = "车次 车站 时间 历时 特等 一等 二等 高级软卧 软卧 动卧 硬卧 软座 硬座 无座 其它".split()


    def __init__(self, available_trains, options):
        """查询到的火车班次集合

        :param available_trains:一个列表，包含可获得的火车班次，每个火车班次是一个字典
        :param options:查询的选项，如高铁，动车，etc
        """

        self.available_trains = available_trains
        self.options = options


    # 将历时转化为小时和分钟的形式
    def get_duration(self, raw_train):
        duration = raw_train[10].replace(':', '小时') + '分'
        #检查是否以00开头，就从字符串第5位开始输出，12306一般有00 : 19这种小于1小时时间
        if duration.startswith('00'):
            return duration[4:]
        if duration.startswith('0'):
            return duration[1:]
        return duration

    def check_equals(self, start_station, end_station, test_station):
        """
        检查是否是始、过、终
        :param start_station: 出发位置
        :param end_station: 到达位置
        :param test_station: 判断位置
        :return: 返回结果
        """ 

        if start_station == test_station:
            return '始'
        elif end_station == test_station:
            return '终'
        else:
            return '过'


    def trains(self):
        # 获取每一条数据
        for raw_train in self.available_trains:
            # 将数据按|分隔
            raw_train = raw_train.split('|')
            # 获取数组中第4列数据
            train_no = raw_train[3]
            # 获取车次对应第一个字母
            initial = train_no[0].lower()
            # 反转station所对应的字典
            station_re = dict(zip(stations.values(), stations.keys()))
            # 如果没有参数或查询车次首字母在opthons中才会显示
            if not self.options or initial in self.options:
                # 分别获取车次始发、终点、查询开始站、查询到达站
                begin_station = station_re.get(raw_train[4])
                end_station = station_re.get(raw_train[5])
                from_station = station_re.get(raw_train[6])
                to_station = station_re.get(raw_train[7])

                # 判断是否为始发、终止、过
                begin_flag = self.check_equals(begin_station, end_station, from_station)
                end_flag = self.check_equals(begin_station, end_station, to_station)

                # 将数据拼接
                train = [
                    train_no,
                    '\n'.join([Fore.GREEN + begin_flag + ' ' + str(from_station) + Fore.RESET,
                               Fore.RED + end_flag + ' ' + str(to_station) + Fore.RESET]),
                    '\n'.join([Fore.GREEN + raw_train[8] + Fore.RESET,
                               Fore.RED + raw_train[9] + Fore.RESET]),

                    self.get_duration(raw_train),

                    # 如果查询到数据不为空就使用否则就是--

                    # 商务座、特等座
                    raw_train[32] if raw_train[32] != "" else "--",

                    # 一等座
                    raw_train[31] if raw_train[31] != "" else "--",

                    # 二等座
                    raw_train[30] if raw_train[30] != "" else "--",

                    # 高级软卧
                    raw_train[21] if raw_train[21] != "" else "--",

                    # 软卧
                    raw_train[23] if raw_train[23] != "" else "--",

                    # 动卧
                    raw_train[33] if raw_train[33] != "" else "--",

                    # 硬卧
                    raw_train[28] if raw_train[28] != "" else "--",

                    # 软座
                    raw_train[24] if raw_train[24] != "" else "--",

                    # 硬座
                    raw_train[29] if raw_train[29] != "" else "--",

                    # 无座
                    raw_train[26] if raw_train[26] != "" else "--",

                    # 其它
                    raw_train[22] if raw_train[22] != "" else "--",
                ]
                yield train

    # 按表格打印
    def pretty_print(self):
        pt = PrettyTable()
        # 设置表格标题
        pt._set_field_names(self.header)
        # 一行一行打印
        for train in self.trains():
            pt.add_row(train)
        print(pt)
        

def cli():
    """command-line interface"""
    # 将绑定交互参数
    arguments = docopt(__doc__)
    from_station = stations.get(arguments['<from>'])
    to_station = stations.get(arguments['<to>'])
    date = arguments['<date>']
    #print(arguments)
    
    # 构建URL
    url = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(
        date, from_station, to_station
    )

    # 获取参数中的key从arguments中，前提为value为True
    options = ''.join([
        key for key, value in arguments.items() if value is True
    ])
    
    r = requests.get(url, verify=False)
    # 以防输入过期的时间    
    #available_trains = r.json()['data']['result'] if 'data' in r.json() else print(r.json()['messages']), sys.exit()
    available_trains = r.json()['data']['result'] 
    TrainsCollection(available_trains, options).pretty_print()

# __name__为__main__时表示程序作为主程序执行，而不是使用import 作为模块导入执行
if __name__ == '__main__':
    cli()
