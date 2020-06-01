import pymongo
import json


def check_ever_crawl(url, board_name):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["ptt_aotter"]
    customers = db[board_name]

    db_url = []
    for x in customers.find({}):
        s1 = json.dumps(x)
        d2 = json.loads(s1)
        db_url.append(d2['_id'])

    if url in set(db_url):
        return "exist"
    else:
        return "No exit in database"
