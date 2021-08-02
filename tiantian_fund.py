from os import urandom
import requests
import json
import re
import pandas as pd
import numpy as np
import math


"""
爬取天天基金数据
"""

cookie = "qgqp_b_id=930878e3fc89b6b43fbe97fe52c17a4c; EMFUND0=null; EMFUND1=null; EMFUND2=null; EMFUND3=null; EMFUND4=null; EMFUND5=null; EMFUND6=null; EMFUND7=null; EMFUND8=null; EMFUND9=05-11 19:25:00@#$%u62DB%u5546%u4E2D%u8BC1%u7164%u70AD%u7B49%u6743%u6307%u6570%28LOF%29@%23%24161724; st_pvi=25460009369036; st_sp=2021-05-07%2015%3A07%3A05; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink"
agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"


#   获取所有基金的代码
def get_all_fund_code():
    url = "http://fund.eastmoney.com/js/fundcode_search.js"

    params = {
        "Cookie": cookie,
        "Referer": "http://fund.eastmoney.com/allfund.html",
        "User-Agent": agent,
        "Host": "fund.eastmoney.com",
    }

    html = requests.get(url, params=params)

    text = re.findall("var r = (.*])", html.text)[0]
    CodeList = json.loads(text)
    all_fund_Code = pd.DataFrame(
        CodeList, columns=["基金代码", "基金名称缩写", "基金名称", "基金类型", "基金名称拼音"]
    )
    all_fund_Code = all_fund_Code.loc[:, ["基金代码", "基金名称", "基金类型"]]

    return all_fund_Code


#   根据基金代码获取total_num个历史净值数据
def get_fund_data(fund_code, total_num=5000):
    url = "http://api.fund.eastmoney.com/f10/lsjz"
    page_size = 20

    NetValueList = []
    TotalCount = 20

    page_idx = 0
    while page_size * page_idx < total_num:
        page_idx += 1

        params = {
            "callback": "jQuery183012799541589289176_1620733013809",
            "fundCode": fund_code,
            "pageIndex": page_idx,
            "pageSize": page_size,
        }

        headers = {
            "Cookie": cookie,
            "Referer": "http://fundf10.eastmoney.com/",
            "User-Agent": agent,
            "Host": "api.fund.eastmoney.com",
        }

        html = requests.get(url, headers=headers, params=params)
        if html.status_code != 200:
            break

        text = re.findall("\((.*?)\)", html.text)[0]
        TotalCount = json.loads(text)["TotalCount"]  # 转化为dict
        total_num = min(total_num, TotalCount)
        if page_size * (page_idx - 1) < total_num:
            NetValueList += json.loads(text)["Data"]["LSJZList"]  # 获取历史净值数据

    # print(fund_code, ' total cnt : ', TotalCount)

    NetValue = pd.DataFrame(NetValueList)  # 转化为DataFrame格式
    if len(NetValueList) != 0:
        NetValue["FundCode"] = fund_code  # 新增一列fundCode
        NetValue = NetValue.loc[:, ["FSRQ", "DWJZ", "LJJZ", "JZZZL", "FundCode"]]

    return NetValue


if __name__ == "__main__":

    data_num = 10
    all_fund_code = get_all_fund_code()
    # for fund_code in all_fund_code['基金代码']:
    #     get_fund_data(fund_code, data_num).to_csv('./fund_data/%s_lsjz.csv' % fund_code, mode='w', index=True, header=True)

    print(get_all_fund_code())
    print(get_fund_data("000001", 10))

    # file = open("web.txt", 'w+', encoding='utf8')
    # file.write('text')
    # file.close()
