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
                "https://www.kickstarter.com" + pro,
            ]
        else:
            print "\n Warning: Project URL is not defined!"
        if pid is not None:
            self.pid = pid
        else:
            print "\n Error_ks_updater: Project ID is not defined!"

    def parse(self, response):

        il = ItemLoader(item=KickstarterUpItem())

        goal_object = response.xpath('//*[@id="stats"]/div/div[2]/span/span[1]/text()').extract()
        if goal_object is not None:
            goal = str(goal_object)
            il.add_value('goal', goal)
        else:
            il.add_value('goal', unicode(-1))

        # TODO: nr. of backers

        pledged_object = response.css('#pledged data::text').extract()
        if pledged_object is not None:
            pledged = str(pledged_object)
            il.add_value('pledged', pledged)
        else:
            il.add_value('pledged', unicode(-1))




        il.add_value('id', self.pid)

        return il.load_item()


