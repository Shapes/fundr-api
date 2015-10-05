# -*- coding: utf-8 -*-

__author__ = 'marko'

import scrapy
from scrapy.loader import ItemLoader
from cfservis.items import KickstarterItem
from scrapy.utils.response import open_in_browser
import re


class KickstarterSpider(scrapy.Spider):
    name = "kickstarter_getter"
    allowed_domains = ["kickstarter.com"]
    start_urls = [
        "https://www.kickstarter.com/discover/categories/art?sort=newest",
    ]
    type = "one"
    category = "unknown"
    categories = (
        'art',
        'comics',
    )
    """
        'crafts',
        'dance',
        'design',
        'fashion',
        'film%20&%20video',
        'food',
        'games',
        'journalism',
        'music',
        'photography',
        'publishing',
        'technology',
        'theater',
    )
    """

    def __init__(self, category=None, type=None, *args, **kwargs):
        super(KickstarterSpider, self).__init__(*args, **kwargs)
        self.category = category
        self.type = type
        if category is not None:
            self.start_urls = [
                "https://www.kickstarter.com/discover/categories/" + category + "?sort=newest",
            ]
        else:
            print "\n Warning: Category is not defined!"
        if self.type == "all":  # parse all categories
            for category in self.categories:
                self.start_urls.append(
                    "https://www.kickstarter.com/discover/categories/" + category + "?sort=newest"
                )

    def parse(self, response):

        if self.type == "all":
            url = str(response.url)
            m = re.search('/[a-z0-9A-Z-]+\?', url)
            if m is not None:
                category = ((m.group(0)).replace("/", "")).replace("?", "")
            else:
                category = "film%20&%20video"
        else:
            category = self.category

        for sel in response.xpath('//*[@id="projects_list"]/li/div'):
            il = ItemLoader(item=KickstarterItem())

            il.add_value('website', 1)

            il.add_value('type', 1)  # TODO ostali tipi?

            pledged = str(sel.css('.project-stats-value span::text').extract())
            il.add_value('pledged', pledged)

            currency = str(sel.css('.project-stats-value span::attr(class)').extract())
            il.add_value('currency', currency)

            author = str(sel.css('.project-byline::text').extract())
            il.add_value('author', author)

            title = str(sel.css('.project-title a::text').extract())
            il.add_value('title', title)

            url = str(sel.css('.project-title a::attr(href)').extract())
            il.add_value('project_url', url)

            il.add_value('id', url)

            img_url = str(sel.css('.project-thumbnail-img::attr(src)').extract())
            il.add_value('img_url', img_url)

            location = str(sel.css('.location-name::text').extract())
            il.add_value('location', location)

            end = str(sel.css('.ksr_page_timer::attr(data-end_time)').extract())
            il.add_value('end', end)

            il.add_value('category_id', category)

            yield il.load_item()


