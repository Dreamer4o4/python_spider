from os import urandom
from pandas.core import indexing
from pandas.core.frame import DataFrame
import requests
import json
import re
import pandas as pd
import numpy as np
import math
import time
import datetime
import threading

cookie = "acw_tc=2760824816279155407552827eb5910e3251282a80465358bd3dad1decf981; channel=undefined; device_id=web_B17TzBFByK; xq_a_token=6a56579f40edefe33cdfa961a04043d21e74a35e; Hm_lvt_d8a99640d3ba3fdec41370651ce9b2ac=1627915541; Hm_lpvt_d8a99640d3ba3fdec41370651ce9b2ac=1627915924; timestamp=1627915924042"
agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"


def get_one_page_personal_fund_code(page_index):
    headers = {
        "Cookie": cookie,
        "Referer": "https://danjuanfunds.com/activity/GroupBigV",
        "User-Agent": agent,
        "Host": "danjuanfunds.com",
    }
    url = (
        "https://danjuanfunds.com/djapi/fundx/portfolio/v3/plan/united/page?tab=4&page="
        + str(page_index)
        + "&size=20&default_order=1&invest_strategy=&type=&manager_type=&yield_between=&mz_between="
    )

    html = requests.get(url, headers=headers)
    if html.status_code != 200:
        print("get_one_page_personal_fund_info error")
        return None

    personal_fund_code_list = json.loads(html.text)["data"]["items"]
    res = pd.DataFrame(personal_fund_code_list).loc[:, ["plan_code", "plan_name"]]
    return res


#   获取所有私人基金组合代码
def get_personal_fund_code(pages=3):
    personal_fund_code_list = []

    if pages < 1:
        return None

    personal_fund_code = get_one_page_personal_fund_code(1)
    for page in range(2, pages + 1):
        personal_fund_code = pd.concat(
            [personal_fund_code, get_one_page_personal_fund_code(page)],
            ignore_index=True,
        )

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

    if int(fund_basic_info["found_days"]) < 365:
        return 0, 0

    # 返回年化收益、近1年收益
    return fund_basic_info["yield_middle"], fund_basic_info["plan_derived"]["nav_grl1y"]


# 简单判断当前私人基金是否值得信任
def analysis_data(annualized_income, one_year_income):
    if float(annualized_income) < 20 or float(one_year_income) < 20:
        return False
    return True


def get_adjust_plan(code):
    headers = {
        "Cookie": cookie,
        "Referer": "https://danjuanfunds.com/strategy/" + code,
        "User-Agent": agent,
        "Host": "danjuanfunds.com",
    }
    url = (
        "https://danjuanfunds.com/djapi/plan/" + code + "/trade_history?size=20&page=1"
    )

    html = requests.get(url, headers=headers)
    if html.status_code != 200:
        print("get_one_page_personal_fund_info error")
        return None

    fund_adjust_info = json.loads(html.text)["data"]["items"][0]

    return fund_adjust_info


def parase_adjust_plan(fund_adjust_info):
    info = ""

    for item in fund_adjust_info["trading_elements"]:
        cur_item_info = (
            item["fd_code"]
            + "|"
            + item["fd_name"]
            + "|"
            + item["last_percent"]
            + "% -> "
            + item["percent"]
            + "%\n"
        )
        if item["last_percent"] > item["percent"]:
            info = info + cur_item_info
        else:
            info = cur_item_info + info

    info = "explain \t: " + fund_adjust_info["remark"] + "\n" + info
    timestamp = int(fund_adjust_info["trade_date"]) / 1000
    info = (
        "time \t\t: " + time.strftime("%Y-%m-%d", time.localtime(timestamp)) + "\n"
    ) + info
    info = "fund code \t: " + fund_adjust_info["plan_code"] + "\n" + info

    return info


def check_one_fund(index, index_info, days=10):
    code = index_info.loc[index].values[0]
    name = index_info.loc[index].values[1]
    # print("cur code : ", code, " ", name)
    annualized_income, one_year_income = get_personal_fund_info(code)
    if analysis_data(annualized_income, one_year_income):
        fund_adjust_info = get_adjust_plan(code)

        if (
            int(fund_adjust_info["trade_date"])
            >= (time.time() - days * 24 * 60 * 60) * 1000
        ):
            parase_data = "fund name \t: " + name + "\n"
            parase_data += parase_adjust_plan(fund_adjust_info)
            return parase_data
    return ""


index_info = []
cur_idx = -1
res = ""
threadLock = threading.Lock()

class MyThread(threading.Thread):
    def __init__(self, past_days=10):
        threading.Thread.__init__(self)
        self.past_days = past_days

    def run(self):
        global index_info, cur_idx, res
        while True:
            threadLock.acquire()
            cur_idx += 1
            threadLock.release()
            if cur_idx >= len(index_info):
                break

            cur_res = check_one_fund(cur_idx, index_info, self.past_days)
            if cur_res != "":
                res += "\n" + cur_res


if __name__ == "__main__":
    index_info = get_personal_fund_code(pages=3)
    # print(index_info)

    # for index in index_info.index:
    #     print(check_one_fund(index, index_info))

    thread_num = 8
    thread_list = []
    for idx in range(thread_num):
        cur_thread = MyThread(past_days=10)
        cur_thread.start()
        thread_list.append(cur_thread)

    for cur_thread in thread_list:
        cur_thread.join()

    # print (res)
    file = open("./out.txt", "w", encoding="utf-8")
    file.write(res)
