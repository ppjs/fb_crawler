# -*- coding: utf-8 -*-
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import time
import csv
import re
import os


class Collector(object):


    def __init__(self, chrome_options=None, mail="", passwd=""):
        super(Collector, self).__init__()
        self.flag_com = "none"
        self.cID = 1
        self.rID = 1
        self.Comments = pd.DataFrame()
        self.Replys = pd.DataFrame()
        # browser instance
        if chrome_options is None:
            chrome_options = Options()
            prefs = {'profile.managed_default_content_settings.images':2, 'disk-cache-size': 4096, 'intl.accept_languages': 'en-US',
                'profile.default_content_setting_values':{'notifications': 2}}
            chrome_options.add_argument('--dns-prefetch-disable')
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--lang=en-US')
            chrome_options.add_argument("disable-infobars") 
            # chrome_options.add_argument('--headless')
            chrome_options.add_experimental_option('prefs', prefs)
        PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
        print(PROJECT_ROOT)
        print()
        self.browser = webdriver.Chrome(executable_path = "./chromedriver", chrome_options=chrome_options)


        self.browser.get("https://mbasic.facebook.com")
        # email 
        context = self.browser.find_element_by_css_selector('#m_login_email')
        context.send_keys(mail)
        time.sleep(0.5)
		# password
        context = self.browser.find_element_by_name('pass')
        context.send_keys(passwd)
        time.sleep(0.5)
        # login-button
        commit = self.browser.find_element_by_name('login')
        commit.click()


        time.sleep(3)


    def clear(self):
        self.Comments = pd.DataFrame()
        self.Replys = pd.DataFrame()
        self.TagUsers = pd.DataFrame()
        self.flag_com = "none"


    # comments
    def collect_coms(self, pID, link):
        self.browser.get(link)
        time.sleep(1)


        comments = self.browser.find_elements_by_xpath("//div[@id='m_story_permalink_view']/div[contains(@class,'e')]/div/div/div[not(contains(@id, 'see_next')) and not(contains(@id, 'see_prev'))]")
        for comment in comments:
            # user_id
            try:
                user_id_str = comment.find_element_by_css_selector("h3 a").get_attribute("href")
                if "profile.php" in user_id_str:
                    user_id = re.search("id=(.+)&rc", user_id_str).group(1)
                else:
                    user_id = user_id_str.split("?")[0].split(".com/")[1]
            except:
                user_id = ""
            # user_name
            try:
                user_name = comment.find_element_by_css_selector("h3").text
            except:
                user_name = ""
            # comment_content
            try:
                comment_content = comment.find_element_by_xpath("div/div").text
            except:
                comment_content = "sticker"
            # comment_time
            try:
                comment_time = comment.find_element_by_css_selector("abbr").text
            except:
                comment_time = ""
            #detect whether replies exist
            replies_container = comment.find_elements_by_xpath("div/div")
            if len(replies_container) == 4:
                # save reply link
                reply_link = reply_link = replies_container[3].find_element_by_css_selector("a").get_attribute("href")
            else:
                reply_link = ""

            df_comment = pd.DataFrame(data = [{'cID': self.cID,
                                               'UserID': user_id,
                                               'UserName': user_name,
                                               'CommentTime': comment_time,
                                               'CommentContent': comment_content,
                                               'pID': pID,
                                               'reply_link': reply_link}],
                                      columns = ['cID', 'UserID', 'UserName', 'CommentTime', 'CommentContent', 'pID', 'reply_link'])
            self.Comments = pd.concat([self.Comments, df_comment], ignore_index=True)
            self.cID += 1


        # comments of next page
        if self.flag_com == "none":
            try:
                next_btn = self.browser.find_element_by_xpath("//div[@id='m_story_permalink_view']/div[contains(@class,'e')]/div/div/div[contains(@id, 'see_next')]/a")
                next_page = next_btn.get_attribute("href")
                self.flag_com = "see_next"
                self.collect_coms(pID, next_page)
            except:
                try:
                    next_btn = self.browser.find_element_by_xpath("//div[@id='m_story_permalink_view']/div[contains(@class,'e')]/div/div/div[contains(@id, 'see_prev')]/a")
                    next_page = next_btn.get_attribute("href")
                    self.flag_com = "see_prev"
                    self.collect_coms(pID, next_page)
                except:
                    return
        else:
            try:
                next_btn = self.browser.find_element_by_xpath("//div[@id='m_story_permalink_view']/div[contains(@class,'e')]/div/div/div[contains(@id, '{}')]/a".format(self.flag_com))
                next_page = next_btn.get_attribute("href")
                self.collect_coms(pID, next_page)
            except:
                return


    # replies of comments
    def collect_reps(self, cID, link):
        self.browser.get(link)
        time.sleep(1)

        replys = self.browser.find_elements_by_xpath("//div[@id='objects_container']/div[contains(@class,'e')]/div[contains(@class,'y')]/div/div[not(contains(@id, 'see_next')) and not(contains(@id, 'see_prev'))]")
        replys_len = len(replys)
        for i in range(1, replys_len):
            reply = replys[i]
            # user_id
            try:
                user_id_str = reply.find_element_by_css_selector("h3 a").get_attribute("href")
                if "profile.php" in user_id_str:
                    user_id = re.search("id=(.+)&rc", user_id_str).group(1)
                else:
                    user_id = user_id_str.split("?")[0].split(".com/")[1]
            except:
                user_id = ""
            # user_name
            try:
                user_name = reply.find_element_by_css_selector("h3").text
            except:
                user_name = ""
            # reply_content
            try:
                reply_content = reply.find_element_by_xpath("div/div").text
            except:
                reply_content = "sticker"
            # reply_time
            try:
                reply_time = reply.find_element_by_css_selector("abbr").text
            except:
                reply_time = ""

            df_reply = pd.DataFrame(data = [{'rID': self.rID, \
                                             'UserID': user_id, \
                                             'UserName': user_name, \
                                             'ReplyTime': reply_time, \
                                             'ReplyContent': reply_content, \
                                             'cID': cID}], \
                                    columns = ['rID', 'UserID', 'UserName', 'ReplyTime', 'ReplyContent', 'cID'])
            self.Replys = pd.concat([self.Replys, df_reply], ignore_index=True)
            self.rID += 1
        try:
            next_btn = self.browser.find_element_by_xpath("//div[@id='objects_container']/div[contains(@class,'e')]/div[contains(@class,'y')]/div/div[contains(@id, 'comment_replies_more_1')]/a")
            next_page = next_btn.get_attribute("href")
            self.collect_reps(cID, next_page)
        except:
            return
