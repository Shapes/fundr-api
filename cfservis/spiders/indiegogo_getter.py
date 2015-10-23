# -*- coding: utf-8 -*-
__author__ = 'marko'

import scrapy
from cfservis.items import IndiegogoItem
from scrapy.utils.response import open_in_browser
import re
from selenium import webdriver
import time
from random import randint
from scrapy.loader import ItemLoader


class IndiegogoSpider(scrapy.Spider):
    name = "indiegogo_getter"
    allowed_domains = ["indiegogo.com"]
    type = "one"
    category = "unknown"
    categories = (
        'animals',
        'art',
        'comics',
        'community',
        'dance',
        'design',
        'education',
        'environment',
        'fashion',
        'film',
        'food',
        'gaming',
        'health',
        'music',
        'photography',
        'publicist',
        'religion',
        'small_business',
        'sports',
        'technology',
        'theatre',
        'video_web',
        'writing',
    )

    start_urls = [
        "https://www.indiegogo.com/explore/animals#/browse/new",
    ]

    def __init__(self, category=None, type=None, *args, **kwargs):
        #self.driver = webdriver.Firefox()
        self.driver = webdriver.PhantomJS()
        self.category = category
        self.type = type
        super(IndiegogoSpider, self).__init__(*args, **kwargs)
        if category is not None:
            self.start_urls = [
                # "https://www.indiegogo.com/explore/" + category + "#/browse/popular_all",
                "https://www.indiegogo.com/explore/" + category + "#/browse/new",
            ]
        else:
            print "\nWarning: Category is not defined!"
        if self.type == "all":  # parse all categories
            for category in self.categories:
                self.start_urls.append(
                    "https://www.indiegogo.com/explore/" + category + "#/browse/new"
                )
            print "You are running multiple spiders at once! Ignore warning above ;)"

    def parse(self, response):
        self.driver.set_window_size(1024, 768)
        self.driver.get(response.url)
        # self.driver.save_screenshot('screen.png')  # make screenshots if using phantomJS as a driver
        time.sleep(4)  # wait for data to load


        # bugfix
        first_option = self.driver.find_element_by_xpath('//div[2]/div/div[2]/a[4]/span')
        if first_option.text == "NEW THIS WEEK":
            first_option.click()
        else:
            self.driver.find_element_by_xpath('//div[2]/div/div[2]/a[3]/span').click()
        time.sleep(4)

        if self.type == "all":
            url = str(response.url)
            m = re.search('re/[a-z0-9A-Z-]+', url)
            if m is not None:
                category = (m.group(0)).replace("re/", "")
                self.category = category
        current_category = self.category

        idx = 0
        while idx < 6:  # TODO: mozno da jih je manj, za doloceno kategorijo?
            indie_projects = self.driver.find_elements_by_class_name("project-card-with-friend-list")
            project = indie_projects[idx]

            il = ItemLoader(item=IndiegogoItem())

            title = (project.find_elements_by_class_name("i-title"))[0].text
            il.add_value('title', title)
            il.add_value('id', 'use title')

            # povezava do slike
            img_wrapper = project.find_element_by_class_name("i-img")
            img_element = img_wrapper.find_element_by_tag_name("img")
            il.add_value('img_url', img_element.get_attribute("src"))

            # povezava do projekta
            a_element = project.find_elements_by_class_name("i-project")[0]
            il.add_value('project_url', a_element.get_attribute("href"))

            # zbrano
            pledged_clip = project.find_element_by_class_name("currency")
            p_element = pledged_clip.find_elements_by_class_name("ng-binding")
            il.add_value('pledged', p_element[0].text)

            il.add_value('currency', p_element[1].text )

            il.add_value('type', 1)
            il.add_value('website', 2)

            # TODO: maybe move this to updater?
            a_element.click()
            time.sleep(randint(3, 6))  # wait for subpage to load

            # -- sub-page
            end_wrapper = self.driver.find_element_by_class_name("i-time-left")
            if end_wrapper.size > 0:
                il.add_value('end', end_wrapper.text)  # TODO: preveri če so ure
            else:
                il.add_value('end', 'endet')

            # TODO: fiksni xpath se spreminja!
            location_city_state = (self.driver.find_elements_by_xpath('//div[3]/div/div[4]/div[2]'))[0].text
            location_country = (self.driver.find_elements_by_xpath('//div[3]/div/div[4]/div[3]'))[0].text

            il.add_value('location', location_city_state)
            il.add_value('location', location_country)

            author = (self.driver.find_elements_by_class_name('i-detailsColumn-title'))[0].text
            il.add_value('author', author)

            self.driver.back()
            # -- main-page

            il.add_value('category_id', current_category)

            idx += 1
            yield il.load_item()

        self.driver.close()

