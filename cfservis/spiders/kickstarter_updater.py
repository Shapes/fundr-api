# -*- coding: utf-8 -*-

__author__ = 'marko'

import scrapy
from scrapy.loader import ItemLoader

from cfservis.items import KickstarterUpItem


class KickstarterSpiderUpdater(scrapy.Spider):
    name = "kickstarter_updater"
    allowed_domains = ["kickstarter.com"]
    start_urls = [
        "https://www.kickstarter.com/projects/ID/IME",
    ]
    project = ""
    pid = 0

    def __init__(self, pro=None, pid=None, *args, **kwargs):
        super(KickstarterSpiderUpdater, self).__init__(*args, **kwargs)
        if pro is not None:
            self.project = pro
            self.start_urls = [
                pro,
            ]
        else:
            print "\n Warning: Project URL is not defined!"
        if pid is not None:
            self.pid = pid
        else:
            print "\n Error_ks_updater: Project ID is not defined!"

    def parse(self, response):

        il = ItemLoader(item=KickstarterUpItem())
        il.add_value('id', self.pid)

        # GOAL
        goal_object = response.xpath('//*[@id="stats"]/div/div[2]/span/span[1]/text()').extract()
        if len(goal_object) is not 0:
            goal = str(goal_object)
            il.add_value('goal', goal)
        else:
            il.add_value('goal', '')

        # TODO: nr. of backers

        # PLEDGED
        pledged_object = response.css('#pledged data::text').extract()
        if len(goal_object) is not 0:
            pledged = str(pledged_object)
            il.add_value('pledged', pledged)
        else:
            sub_page = response.url + "/description"
            request = scrapy.Request(sub_page, callback=self.parse_description)
            request.meta['item'] = il
            return request

        return il.load_item()

    def parse_description(self, response):
        il = response.meta['item']
        final_pledged_object = response.xpath('//*[@id="content-wrap"]/div[3]/section[1]/div/div/div/div/d'
                                                  'iv[1]/div[1]/div/div[2]/h3/span/text()').extract()
        pledged = str(final_pledged_object)
        il.add_value('pledged', pledged)
        return il.load_item()
