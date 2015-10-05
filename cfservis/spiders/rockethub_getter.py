# -*- coding: utf-8 -*-
__author__ = 'marko'

import scrapy
from cfservis.items import RockethubItem
from scrapy.utils.response import open_in_browser
import re
from selenium import webdriver
import time
from scrapy.loader import ItemLoader
from random import randint


class RockethubSpider(scrapy.Spider):
    name = "rockethub_getter"
    allowed_domains = ["rockethub.com"]
    start_urls = [
        "https://www.rockethub.com/projects?cats_secondary=1",
    ]
    type = "one"
    category = "100"
    categories = (
        '1',
        '2',
        '3', '4', '5', '6'
    )
    """
        '7', '8', '9', '10',
        '11', '12', '13', '14',
        '15', '17', '18',
        '19', '20', '21', '22',
        '23', '24', '25', '26',
        '27', '28', '30',
        '35', '36', '37', '38',
        '41'
    )
    """

    def __init__(self, category=None, type=None, *args, **kwargs):
        self.driver = webdriver.Firefox()
        #self.driver = webdriver.PhantomJS()
        self.category = category
        self.type = type
        super(RockethubSpider, self).__init__(*args, **kwargs)
        if category is not None:
            self.start_urls = [
                "https://www.rockethub.com/projects?cats_secondary=" + category,
            ]
        else:
            print "Warning: Category is not defined!"
        if self.type == "all":  # parse all categories
            for category in self.categories:
                self.start_urls.append(
                    "https://www.rockethub.com/projects?cats_secondary=" + category
                )
            print "You are running multiple spiders at once! Ignore warning above ;)"

    def parse(self, response):
        self.driver.get(response.url)
        time.sleep(3)  # wait for data to load

        # show hidden overlays, inject some js code
        # TODO: Do i need this?
        injection_script = "elements = document.getElementsByClassName('overlay');" \
                           "for (var i=0;i<elements.length;i++){ elements[i].style.display = 'block'; }"
        self.driver.execute_script(injection_script)

        if self.type == "all":
            url = str(response.url)
            m = re.search('y=[a-z0-9A-Z-]+', url)
            if m is not None:
                category = (m.group(0)).replace("y=", "")
                self.category = category
        current_category = self.category

        idx = 0
        while idx < 9:  # TODO: mozno da jih je manj, za doloceno kategorijo
            indie_projects = self.driver.find_elements_by_class_name("project-box")
            project = indie_projects[idx]
            il = ItemLoader(item=RockethubItem())

            summary_wrapper = project.find_element_by_class_name('summary')
            title = summary_wrapper.find_element_by_tag_name('h1').text
            il.add_value('title', title)

            author = summary_wrapper.find_element_by_tag_name('h2').text
            il.add_value('author', author)

            pid = project.get_attribute('id')[8:]
            il.add_value('id', pid)

            picture_wrapper = project.find_element_by_class_name('picture')
            p = picture_wrapper.find_element_by_tag_name('a')
            project_url = p.get_attribute('href')
            il.add_value('project_url', project_url)

            p = picture_wrapper.find_element_by_tag_name('img')
            img_url = p.get_attribute('src')
            il.add_value('img_url', img_url)

            #  -- overlay

            # TODO: test if not already endet?
            end = project.find_element_by_class_name('days-left-count').text + "days"  # TODO: if hours
            il.add_value('end', end)

            il.add_value('type', 1)
            il.add_value('website', 3)
            il.add_value('currency', 'USD')

            pledged_element = project.find_element_by_class_name('dollars')
            il.add_value('pledged', pledged_element.text)

            locations = project.find_elements_by_class_name('location')
            if len(locations) > 0:
                il.add_value('location', locations[0].text)
            else:
                il.add_value('location', 'no location')

            # -- /

            il.add_value('category_id', current_category)

            idx += 1
            yield il.load_item()

        self.driver.close()

