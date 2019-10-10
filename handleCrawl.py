# -*- coding: utf-8 -*-  
import requests
import urllib
from bs4 import BeautifulSoup
import json
import os, sys
import re

def convertTitleToLink(title):
    title = re.sub(r"[()\"#@;:<>{}`+=~|.!?,\[\]]", "", title)
    while "  " in title:
        title = title.replace("  ", " ")
    title = title.replace(' ','-').replace('/','-').lower()
    while "--" in title:
        title = title.replace("--", "-")
    title = title.replace("\n", "")
    return title

def crawlSearch(keyword, number):
    query_string = urllib.parse.urlencode({"search_query": keyword.encode("utf-8")})
    page = requests.get("https://www.youtube.com/results?q={}&page={}".format(query_string, number))
    soup = BeautifulSoup(page.content, 'html.parser', from_encoding="utf-8")
    #  = soup.prettify()
    # with open("crawl/search.html", "wb") as html:
    #     html.write(soup_.encode('utf-8'))
    display = []
    try:
        for vid in soup.find_all(class_="yt-lockup-dismissable"):
            searchResult = {}
            uid = vid.find("a")["href"][9:]
            if uid.find('list') == -1:
                searchResult['uid'] = uid
                searchResult['title'] = vid.find(class_="yt-lockup-title").find("a").get_text()
                searchResult['link'] = "/video/{}/{}.html".format(searchResult['uid'], convertTitleToLink(searchResult['title']))
                vid_s = vid.find(class_="yt-lockup-meta-info").find_all("li")
                searchResult['timePublish'] = vid_s[0].get_text()
                searchResult['viewCount'] = vid_s[-1].get_text()
                try:
                    searchResult['duration'] = vid.find(class_="video-time").get_text()
                except:
                    searchResult['duration'] = "LIVE"
                    searchResult['timePublish'] = "LIVE"
                searchResult['channel'] = {}
                searchResult['channel']['name'] = vid.find(class_="yt-lockup-byline").find("a").get_text()
                searchResult['channel']['link'] = vid.find(class_="yt-lockup-byline").find("a")['href']
                display.append(searchResult)
    except Exception as e:
        _, _, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        display = {"error": "error: {}, file: {}, line: {}".format(e, fname, exc_tb.tb_lineno)}
    return display

def crawlWatch(uid):
    page = requests.get("https://www.youtube.com/watch?v="+uid)
    soup = BeautifulSoup(page.content, 'html.parser', from_encoding="utf-8")
    # soup_ = soup.prettify()
    # with open("crawl/watch.html", "wb") as html:
    #     html.write(soup_.encode('utf-8'))
    video_data = {}
    try:
        video_data['uid'] = uid
        video_data['title'] = soup.find("span", { "class": "watch-title" }).get_text().replace("\n", "").replace("  ", "")
        video_data['link'] = "/video/{}/{}.html".format(video_data['uid'], convertTitleToLink(video_data['title']))
        video_data['description'] = soup.find("p", { "id" : "eow-description" }).get_text()
        video_data['viewCount'] = soup.find("div", { "class": "watch-view-count" }).get_text()
        video_data['channel'] = {}
        video_data['channel']['name'] = soup.find(class_="yt-uix-sessionlink spf-link").get_text()
        video_data['channel']['link'] = soup.find(class_="yt-uix-sessionlink spf-link")['href']
        video_data['keywords'] = []
        keywords = soup.find_all("meta",  property="og:video:tag")
        for keyword in keywords:
            keyword_format = {}
            keyword_format['keyword'] = keyword["content"]
            keyword_format['link'] = "/tags/" + keyword["content"].replace(" ", "-")
            video_data['keywords'].append(keyword_format)
        video_data['related'] = []
        vids = soup.find_all(class_="video-list-item related-list-item show-video-time") + soup.find_all(class_="video-list-item related-list-item show-video-time related-list-item-compact-video")
        for vid in vids:
            related = {}
            related['uid'] = vid.find(class_="content-wrapper").find("a")["href"][9:]
            related['title'] = vid.find(class_="content-wrapper").find("a")["title"]
            related['link'] = "/video/{}/{}.html".format(related['uid'], convertTitleToLink(related['title']))
            related['channel'] = {}
            related['channel']['name'] = vid.find(class_="stat attribution").get_text()
            related['channel']['link'] = ""
            related['viewCount'] = vid.find(class_="content-wrapper").find(class_="stat view-count").get_text()
            try:
                related['duration'] = vid.find(class_="thumb-wrapper").find(class_="video-time").get_text()
            except:
                related['duration'] = 'LIVE'
            video_data['related'].append(related)
        video_data['comment'] = []
    except Exception as e:
        _, _, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        video_data = {"error": "error: {}, file: {}, line: {}".format(e, fname, exc_tb.tb_lineno)}
    return video_data

def crawlChannel(uid):
    page = requests.get("https://www.youtube.com/channel/"+uid+"/videos?view=0&sort=p&flow=grid")
    soup = BeautifulSoup(page.content, 'html.parser', from_encoding="utf-8")
    # soup_ = soup.prettify()
    # with open("crawl/channel.html", "wb") as html:
    #     html.write(soup_.encode('utf-8'))
    data_channel = {}
    try:
        data_channel['uid'] = uid
        data_channel['name'] = soup.find("a", { "class": "spf-link branded-page-header-title-link yt-uix-sessionlink" }).get_text()
        try:
            data_channel['subscribers'] = soup.find("span", { "class": "yt-subscription-button-subscriber-count-branded-horizontal subscribed yt-uix-tooltip" }).get_text() + ' subscribers'
        except:
            data_channel['subscribers'] = ""
        data_channel['avatar'] = soup.find("img", { "class": "channel-header-profile-image" })['src']
        result = soup.find('div',attrs={'id':'gh-banner'}).find("style").get_text()
        if result is not None:
            data_channel['profile_image'] = "https:" + re.search(r'url\((.+)\)', result).group(1)
        data_channel_videos = []
        for vid in soup.find_all(class_="yt-lockup clearfix yt-lockup-video yt-lockup-grid vve-check"):
            data_videos = {}
            data_videos['uid'] = vid.find(class_="yt-lockup-content").find("a")["href"][9:]
            data_videos['title'] = vid.find(class_="yt-lockup-content").find("a")["title"]
            data_videos['link'] = "/video/" + data_videos['uid'] + "/" + convertTitleToLink(data_videos['title']) + ".html"
            data_videos['thumbnail'] = "http://img.youtube.com/vi/%s/0.jpg" % uid
            vid_s = vid.find(class_="yt-lockup-meta-info").find_all("li")
            data_videos['timePublish'] = vid_s[-1].get_text()
            data_videos['viewCount'] = vid_s[0].get_text()
            try:
                data_videos['duration'] = vid.find(class_="video-time").get_text()
            except:
                data_videos['duration'] = "LIVE"
                data_videos['timePublish'] = "LIVE"
            data_channel_videos.append(data_videos)
        data_channel['videos'] = data_channel_videos
    except Exception as e:
        _, _, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        data_channel = {"error": "error: {}, file: {}, line: {}".format(e, fname, exc_tb.tb_lineno)}
    return data_channel