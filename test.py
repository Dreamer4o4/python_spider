from os import urandom
import requests
import json
import re
import pandas as pd
import numpy as np
import math

def get_one_page(url):
    # 添加headers 绕过反扒
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    }
 
    response = requests.get(url,headers=headers)
    response.encoding = 'utf-8'
    if response.status_code == 200:
        return response.text
    else:
        print("请求状态码 != 200,url错误.")
        return None

def get_fund_data(fund_code, total_num):
    url = "http://api.fund.eastmoney.com/f10/lsjz"
    page_size = 20
    cookie = 'qgqp_b_id=930878e3fc89b6b43fbe97fe52c17a4c; EMFUND0=null; EMFUND1=null; EMFUND2=null; EMFUND3=null; EMFUND4=null; EMFUND5=null; EMFUND6=null; EMFUND7=null; EMFUND8=null; EMFUND9=05-11 19:25:00@#$%u62DB%u5546%u4E2D%u8BC1%u7164%u70AD%u7B49%u6743%u6307%u6570%28LOF%29@%23%24161724; st_pvi=25460009369036; st_sp=2021-05-07%2015%3A07%3A05; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink'
    total_page = math.ceil(total_num / page_size)

    LSJZList = []
    TotalCount = 0

    for page_idx in range(1, total_page + 1):
        print('cur page : ', page_idx)

        params = {
            'callback'  :   'jQuery183012799541589289176_1620733013809',
            'fundCode'  :   fund_code,
            'pageIndex' :   page_idx,
            'pageSize'  :   page_size,
        }

        headers = {
            'Cookie'    :   cookie,
            'Referer'   :   'http://fundf10.eastmoney.com/',
            'User-Agent':   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            'Host'      :   'api.fund.eastmoney.com'
        }

        html = requests.get(url, headers=headers, params=params)

        text = re.findall('\((.*?)\)', html.text)[0]  # 提取dict
        LSJZList += json.loads(text)['Data']['LSJZList']  # 获取历史净值数据
        TotalCount = json.loads(text)['TotalCount']  # 转化为dict
    

    LSJZ = pd.DataFrame(LSJZList)  # 转化为DataFrame格式
    LSJZ['FundCode'] = fund_code  # 新增一列fundCode

    return LSJZ

if __name__ == '__main__':
    
    text = get_fund_data('000001', 100)
    print(text)
    # file = open("web.txt", 'w+', encoding='utf8')
    # file.write(text)
    # file.close()
