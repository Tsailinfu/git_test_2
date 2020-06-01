import requests  # pip install requests
from bs4 import BeautifulSoup  # pip install BeautifulSoup4
import csv

with open('hotboards.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)

r = requests.Session()
r2 = r.get("https://www.ptt.cc/bbs/hotboards.html").text
html = BeautifulSoup(r2)
contents = html.find_all("div", class_="board-name")

for content in contents:
    print(content.text)
    with open('hotboards.csv', 'a+', newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow([content.text])
