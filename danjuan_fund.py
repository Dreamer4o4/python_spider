from os import urandom
from pandas.core import indexing
import requests
import json
import re
import pandas as pd
import numpy as np
import math


'''
爬取蛋卷基金数据
'''

cookie = 'device_id=web_HySymaLOd; timestamp=1621255222027; Hm_lvt_b53ede02df3afea0608038748f4c9f36=1620656862,1620878922,1621001013; channel=1300100141; xq_a_token=aa9076b9f80ed90ceafa820bc88222ef59ba0710; Hm_lpvt_b53ede02df3afea0608038748f4c9f36=1621254084; acw_tc=2760776216212538710955820e0a10884d1ebf68a5faff851f18db5c8963a9'
agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
day = ['3y', '5y', 'all']

def get_index_fund_info():
        url = 'https://danjuanapp.com/djapi/index_eva/dj'

        headers = {
                'Cookie'    :   cookie,
                'Referer'   :   'https://danjuanapp.com/djmodule/value-center?channel=1300100141',
                'User-Agent':   agent,
                'Host'      :   'danjuanapp.com'
        }

        html = requests.get(url, headers=headers)
        if html.status_code != 200:
                print('get_index_fund_code error')
                return None
        
        all_data_list = json.loads(html.text)['data']['items']
        all_data = pd.DataFrame(all_data_list).loc[:, ['index_code', 'name']]
        return all_data
        

#       only pe data
def get_index_fund_data(fund_code, day = day[2]):
        url = "https://danjuanapp.com/djapi/index_eva/pe_history/" + fund_code

        headers = {
                'Cookie'        :       cookie,
                'Referer'       :       'https://danjuanapp.com/dj-valuation-table-detail/' + fund_code,
                'User-Agent'    :       agent,
                'Host'          :       'danjuanapp.com'
        }

        params = {
                'day'           :       day
        }

        html = requests.get(url, headers=headers, params=params)
        if html.status_code != 200:
                print('get_index_fund_data error')
                return None
        
        all_data_list = json.loads(html.text)['data']
        pe_data = pd.DataFrame(all_data_list['index_eva_pe_growths'])
        pe_horizontal_line = pd.DataFrame(all_data_list['horizontal_lines']).loc[:, ['line_name', 'line_value']]
        pe_horizontal_line['day'] = day

        return pe_data, pe_horizontal_line

def cal_basic_info(data):
        sort_data = data.sort_values(by='pe', ascending=True)
        data_list = sort_data['pe'].to_list()
        percent = [0.3, 0.5, 0.7]
        lines = []
        for i in range(3):
               lines.append(data_list[math.ceil(len(data_list) * percent[i])])
        
        return lines

def analysis_data(data):
        horizontal_lines = cal_basic_info(data)

        ##      低于30分位
        if data.iloc[-1:,0].values[0] < horizontal_lines[0]:
                return True
        return False

if __name__ == '__main__':
        index_info = get_index_fund_info()
        # print(index_info)

        for idx in index_info.index:
                info = index_info.loc[idx].values
                data, lines = get_index_fund_data(info[0], day[1])

                if analysis_data(data):
                        print(info[1])


        # data, lines = get_index_fund_data('SPACEVCP')
        # analysis_data(data)
        


        