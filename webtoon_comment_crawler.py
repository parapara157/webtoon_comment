import re
import json
import time
import argparse
import requests
import pathlib2

from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

#mysql에 댓글 저장 원할 시 밑의 주석 해제
#import pymysql
#from config.mysql_config import mysql_info


def getPage(url):
    req = requests.get(url)
    return BeautifulSoup(req.text, 'html.parser')


def get_all_webtoon_links(url):
    bs = getPage(url)
    all_webtoon_links = []

    for daily_webtoons in bs.find_all('div', {'class': 'col'}):
        for webtoon in daily_webtoons.find_all('div', {'class': 'thumb'}):
            webtoon_link = webtoon.find('a')['href']
            all_webtoon_links.append(webtoon_link)
    return all_webtoon_links


def get_title(url):
    bs = getPage(url)
    title = bs.find('title').get_text().split(':')[0]
    return title


def get_titleId(url):
    return parse_qs(urlparse(url).query)['titleId'][0]


def get_all_episode_link(url, number_of_episode):
    bs = getPage(url)
    last_episode_link = bs.find('td', {'class':'title'}).find('a')['href']
    last_episode_no = int(parse_qs(urlparse(last_episode_link).query)['no'][0])
    reg = re.compile('no=.*&')
    all_episode_link = [re.sub(reg, 'no=' + str(i) + '&', last_episode_link) for i in range(last_episode_no, last_episode_no-(number_of_episode), -1) if i > 0]
    return all_episode_link


def get_episode_no(url):
    return parse_qs(urlparse(url).query)['no'][0]


def save_comments(title, titleId, episode_no):
    comment_page = 1
    all_comments = []
    while True:
        commentList = get_commentList(title, titleId, episode_no, comment_page)
        if commentList:
            for comment in commentList:
                all_comments.append(comment['contents'].replace("\n",""))
        else:
            # mysql에 댓글 저장 원할 시 밑의 주석 해제
            #send_mysql(title, episode_no, all_comments)
            write_all_comments(title, episode_no, all_comments)
            return
        comment_page = comment_page + 1


def write_all_comments(title, episode_no, all_comments):
    pathlib2.Path("./data").mkdir(exist_ok=True, parents=True)
    f = open('./data/naver_webtoon_comments.txt', 'a', encoding="utf-8")
    try:
        for comment in all_comments:
            f.write(title + ',' + episode_no + ',' + comment + "\n")
    finally:
        f.close()


def send_mysql(title, episode_no, all_comments):
    conn = pymysql.connect(host=mysql_info['host'], user=mysql_info['user'], passwd=mysql_info['passwd'], db=mysql_info['db'])
    cur = conn.cursor()
    cur.execute('USE naver')
    for comment in all_comments:
        cur.execute('INSERT INTO COMMENT (title, episode_no, comment) VALUES (%s, %s, %s)', (title, episode_no, comment))
    cur.connection.commit()
    cur.close()
    conn.close()


def get_commentList(title, titleId, episode_no, comment_page):
    ajax_link = 'https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json?ticket=comic&templateId=webtoon' + \
                '&pool=cbox3&_callback=jQuery112409768039369695578_1588773317723&lang=ko&country=KR&objectId=' + \
                titleId + '_' + episode_no + '&categoryId=&pageSize=100&indexSize=10&groupId=&listType=OBJECT&pageType=default&page=' + str(comment_page) + \
                '&refresh=true&sort=new&cleanbotGrade=2&_=1588773317725'
    custom_header = {
        'referer': 'https://comic.naver.com/comment/comment.nhn?titleId=' + titleId + '&no=' + episode_no,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
    }
    req = requests.get(ajax_link, headers=custom_header).text
    json_req = json.loads(req[req.find("success") - 2:len(req) - 2])
    commentList = json_req['result']['commentList']
    return commentList


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--number_of_episode', required=False, default=51)
    args = parser.parse_args()

    naver_webtoon_link = 'https://comic.naver.com'
    naver_webtoon_list_link = 'https://comic.naver.com/webtoon/weekday.nhn'
    all_webtoon_links = get_all_webtoon_links(naver_webtoon_list_link)

    for webtoon_link in all_webtoon_links:
        absolute_path = naver_webtoon_link + webtoon_link
        title = get_title(absolute_path)
        titleId = get_titleId(absolute_path)
        all_episode_link = get_all_episode_link(absolute_path, int(args.number_of_episode))

        for episode_link in all_episode_link:
            episode_no = get_episode_no(episode_link)
            comments = save_comments(title, titleId, episode_no)
            print(title, episode_no)
            print("Sleep 1 seconds from now on...")
            time.sleep(1)