from os import urandom
from pandas.core import indexing
import requests
import json
import re
import pandas as pd
import numpy as np
import math

cookie = "acw_tc=2760824816279155407552827eb5910e3251282a80465358bd3dad1decf981; channel=undefined; device_id=web_B17TzBFByK; xq_a_token=6a56579f40edefe33cdfa961a04043d21e74a35e; Hm_lvt_d8a99640d3ba3fdec41370651ce9b2ac=1627915541; Hm_lpvt_d8a99640d3ba3fdec41370651ce9b2ac=1627915924; timestamp=1627915924042"
agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"

def get_one_page_personal_fund_code(page_index):
    headers = {
        "Cookie": cookie,
        "Referer": "https://danjuanfunds.com/activity/GroupBigV",
        "User-Agent": agent,
        "Host": "danjuanfunds.com",
    }
    url = "https://danjuanfunds.com/djapi/fundx/portfolio/v3/plan/united/page?tab=4&page=" + str(page_index) + "&size=20&default_order=1&invest_strategy=&type=&manager_type=&yield_between=&mz_between="

    html = requests.get(url, headers=headers)
    if html.status_code != 200:
        print("get_one_page_personal_fund_info error")
        return None

    personal_fund_code_list = json.loads(html.text)["data"]["items"]
    res = pd.DataFrame(personal_fund_code_list).loc[:, ["plan_code", "plan_name"]]
    return res

#   获取所有私人基金组合代码
def get_personal_fund_code(pages = 3):
    personal_fund_code_list = []

    if pages < 1: 
        return None

    personal_fund_code = get_one_page_personal_fund_code(1)
    for page in range(2, pages + 1):
        personal_fund_code = pd.concat([personal_fund_code, get_one_page_personal_fund_code(page)],ignore_index=True)

    return personal_fund_code

def get_personal_fund_info(code):
    headers = {
        "Cookie": cookie,
        "Referer": "https://danjuanfunds.com/strategy/" + code,
        "User-Agent": agent,
        "Host": "danjuanfunds.com",
    }
    url = "https://danjuanfunds.com/djapi/plan/" + code

    html = requests.get(url, headers=headers)
    if html.status_code != 200:
        print("get_one_page_personal_fund_info error")
        return None

    fund_basic_info = json.loads(html.text)["data"]
    print (fund_basic_info)

    
    return None

if __name__ == "__main__":
    index_info = get_personal_fund_code()
    print(index_info)

    print(index_info.loc[0].values[0])
    get_personal_fund_info(index_info.loc[0].values[0])