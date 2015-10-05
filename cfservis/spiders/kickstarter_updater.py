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

        goal = str(response.xpath('//*[@id="stats"]/div/div[2]/span/span[1]/text()').extract())
        il.add_value('goal', goal)

        # TODO: nr. of backers
        pledged = str(response.css('#pledged data::text').extract())
        il.add_value('pledged', pledged)

        il.add_value('id', self.pid)

        return il.load_item()


