from urllib.parse import urlencode
from fake_useragent import UserAgent
from lxml.html import fromstring
from concurrent.futures import ThreadPoolExecutor

import time
import requests
from bs4 import BeautifulSoup
import random

# 使用代理避免触发网站的访问限制策略
proxies = [
    { 'http': 'http://@zproxy.lum-superproxy.io:22225'},
    { 'http': 'http://:@smartproxy.proxycrawl.com:8012'},
]

# 多线程访问，加快速度
pool = ThreadPoolExecutor(max_workers=20)

def get_name_score(name):

    index = random.randrange(len(proxies))
    proxy = proxies[index]
    # print(proxy)

    print("rating: " + name + ", with proxy%s" % index)

    url = "http://life.httpcn.com/xingming.asp"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "x-lum-onboarding": "xxxxx",
    }

    data = {}
    try:
        data = {
            "data_type": 0,
            "year": 2000,
            "month": 0,
            "day": 0,
            "hour": 0,
            "minute": 0,
            "pid": "北京".encode("gb2312"),
            "cid": "北京".encode("gb2312"),
            "wxxy": 0,
            "xishen": "土".encode("gb2312"),
            "yongshen": "金".encode("gb2312"),
            "xing": "特".encode("gb2312"),
            "ming": name.encode("gb2312"),
            "sex": 1,
            "act": "submit",
            "isbz": 1
        }
    except UnicodeEncodeError as e:
        # 存在一些繁体字无法转换
        # print(e)
        return "failed", "gb2312"

    params_data = urlencode(data)
    # print(params_data)
    try:
        r = requests.post(url, data=params_data, headers=headers, proxies=proxy, verify=False)
        r.encoding = 'gb2312'
    except Exception as e:
        # 代理失效，网络波动
        # print(e)
        return get_name_score(name)

    if r.status_code > 500:
        # 代理失效，网络波动
        # print(r)
        # print(r.text)
        return get_name_score(name)

    if r.status_code != 200:
        # 网站本身返回错误
        # print(r)
        # print(r.text)
        time.sleep(2)
        return get_name_score(name)
        # raise Exception()

    # print(r.text)
    soup = BeautifulSoup(r.text, "html.parser")
    for node in soup.find_all("div", class_="chaxun_b"):
        # print(node)
        if "姓名五格评分" not in node.get_text():
            continue
        score_fonts = node.find_all("font")
        wuge_score = score_fonts[0].get_text()
        bazi_score = score_fonts[1].get_text()
        return wuge_score.replace("分", "").strip(), bazi_score.replace("分", "").strip()

    # 网站本身没有返回评分，可重试
    # print("retry")
    return get_name_score(name)
    # return "failed", "return_blank"

with open("input.txt") as fin, open("output.txt", "w") as fout:
    def handle_name_score(line):
        wuge, bazi = get_name_score(line)
        result = "\t".join(["特%s" % line, wuge, bazi])
        fout.write(result + "\n")
        fout.flush()
        return result

    lines = []
    for line in fin:
        line = line.strip()
        if not line or len(line) == 0:
            continue
        lines.append(line)

    for result in pool.map(handle_name_score, lines):
        # Do whatever you want with the results ...
        print(result)
