import requests  # pip install requests
from bs4 import BeautifulSoup  # pip install BeautifulSoup4
import csv
import re
import time
import warnings
from upload_db_1 import upload_db
from check_ever_crawl_1 import check_ever_crawl
warnings.filterwarnings('ignore')
with open('hotboards.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    data = list(reader)
print(len(data))

for i in range(0, len(data), 1):
    board_name = data[i][0]
    print(board_name)

    r = requests.Session()
    payload = {"from": "/bbs/" + str(board_name) + "/index.html", "yes": "yes"}
    r1 = r.post("https://www.ptt.cc/ask/over18?from=%2Fbbs%2FGossiping%2Findex.html", payload)
    url_2 = "https://www.ptt.cc/bbs/" + str(board_name) + "/index.html"
    r2 = r.get(url_2).text
    html = BeautifulSoup(r2)

    # 按上一頁, 取得網址 index 編號, 並加一後得到現在網址 index 編號,
    contents_lastpage = html.find_all("a", class_="btn wide")
    contents_lastpage_url = contents_lastpage[1]['href']
    print(contents_lastpage_url)

    pattern = re.compile(r'(?<=index)\d+')
    lastpage_index = pattern.findall(contents_lastpage_url)
    nowpage_index = int(lastpage_index[0]) + 1
    print(nowpage_index)

    for i in range(0, 2, 1):
        # 目前整理出現在的網址
        print(nowpage_index)
        now_url = "https://www.ptt.cc/bbs/" + str(board_name) + "/index" + str(nowpage_index) + ".html"
        print(now_url)

        r3 = r.get(now_url).text
        html_3 = BeautifulSoup(r3)
        net_lists = html_3.find_all("div", class_="title")

        for net_list in net_lists:
            # 可能發生本文被刪除, 會沒有連結網址, 導致 href 無法匹配
            try:
                class_list_net = net_list.find("a")['href']
                class_list_net = "https://www.ptt.cc/" + class_list_net
                print(class_list_net)
                whether_exit = check_ever_crawl(class_list_net, board_name)
                print(whether_exit)
                if whether_exit == "exist":
                    continue
                upload_db(class_list_net, board_name)
            except:
                print("pass this article")
        nowpage_index = nowpage_index - 1
        time.sleep(5)
