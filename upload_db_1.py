from urllib.request import urlopen, Request
import requests
from bs4 import BeautifulSoup
import warnings
import datetime
from pymongo import MongoClient
warnings.filterwarnings('ignore')

def upload_db(url, board_name):
    url = url
    r = Request(url)
    r.add_header("user-agent", "Mozilla/5.0")

    jar = requests.cookies.RequestsCookieJar()
    jar.set("over18", "1", domain="www.ptt.cc")
    response = requests.get(url, cookies=jar).text

    html = BeautifulSoup(response)
    content = html.find("div", id="main-content")

    r = requests.Session()
    payload = {"from": "/bbs/" + str(board_name) + "/index.html", "yes": "yes"}

    r1 = r.post("https://www.ptt.cc/ask/over18?from=%2Fbbs%2FGossiping%2Findex.html", payload)
    # print("--------------------------------------------------")
    r2 = r.get(url).text
    html = BeautifulSoup(r2)
    content_html = html.find("div", id="main-content")
    value = content_html.find_all("span", class_="article-meta-value")
    # --------------------
    authorId_authorName = value[0].text
    authorId = authorId_authorName.split(" ")[0]
    # print(authorId)
    # --------------------
    authorName = authorId_authorName.split(" ")[1][1:-1]
    # print(authorName)
    # --------------------
    title = value[2].text
    title = title.split(" ")[1]
    # print(title)
    # --------------------
    t = datetime.datetime.strptime(value[3].text, "%a %b %d %H:%M:%S %Y")
    t_ms = t.timestamp() * 1000
    t_ms = int(t_ms)
    # print(t_ms)
    # print("--------------------------------------------------")
    content = list(content_html)[4]
    # print(content)
    # print("--------------------------------------------------")
    pushes = content_html.find_all("div", class_="push")

    comment = []
    for single_push in pushes:
        commentId = single_push.find("span", class_="push-userid").text
        # print(commentId)
        commentContent = single_push.find("span", class_="push-content").text
        commentContent = commentContent[2:]
        # print(commentContent)
        ipdatetime = single_push.find("span", class_="push-ipdatetime").text

        # 注意跨年問題 commentTime 需大於 publishedTime
        year = value[3].text[-4:]
        # 有些 網頁的評論沒有 ip
        if len(ipdatetime.strip().split(" ")) == 3:
            month = ipdatetime.strip().split(" ")[1][0:2]
            date = ipdatetime.strip().split(" ")[1][3:5]
            hour = ipdatetime.strip().split(" ")[2][0:2]
            minute = ipdatetime.strip().split(" ")[2][3:5]
        elif len(ipdatetime.strip().split(" ")) == 2:
            month = ipdatetime.strip().split(" ")[0][0:2]
            date = ipdatetime.strip().split(" ")[0][3:5]
            hour = ipdatetime.strip().split(" ")[1][0:2]
            minute = ipdatetime.strip().split(" ")[1][3:5]
        # --------------------------------------------------
        date_comment = datetime.datetime(int(year), int(month), int(date), int(hour), int(minute))
        date_comment = datetime.datetime.timestamp(date_comment)
        date_comment = date_comment * 1000
        date_comment = int(date_comment)
        # --------------------------------------------------
        # 遇到跨年份, 評論時間不可早於發文時間:
        if date_comment - t_ms < 0:
            date_comment = datetime.datetime(int(year) + 1, int(month), int(date), int(hour), int(minute))
            date_comment = datetime.datetime.timestamp(date_comment)
            date_comment = date_comment * 1000
            date_comment = int(date_comment)
        value_comment = {"commentId": str(commentId), "commentContent": str(commentContent), "date_comment": int(date_comment)}
        comment.append(value_comment)
    comment_length = len(comment)

    connection = MongoClient(host='localhost', port=27017)
    db = connection.ptt_aotter  # use database as name as : news
    collection_1 = db[board_name]  # create collection score_col

    each_row = {'_id': url,
                'authorId': authorId,
                'authorName': authorName,
                'title': title,
                'publishedTime': t_ms,
                'content': content,
                'canonicalUrl': url,
                'createdTime': None,
                'updateTime': None,
                'comment': comment,
                'comment_length': comment_length
                }

    try:
        collection_1.insert([each_row])
        print("已新增", each_row)
    except:
        print("已經存在 _id: ", each_row['_id'], "(因此不寫入)")
