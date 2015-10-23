# -*- coding: utf-8 -*-

__author__ = 'marko'

import scrapy
from scrapy.loader import ItemLoader

from cfservis.items import RockethubUpItem


class RockethubSpiderUpdater(scrapy.Spider):
    name = "rockethub_updater"
    allowed_domains = ["rockethub.com"]
    start_urls = [
        "https://www.rockethub.com/projects/ID-NAME",
    ]
    project = ""
    pid = ""

    def __init__(self, pro=None, pid=None, *args, **kwargs):
        super(RockethubSpiderUpdater, self).__init__(*args, **kwargs)
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
            print "\n Error_rh_updater: Project ID is not defined!"


    def parse(self, response):
        il = ItemLoader(item=RockethubUpItem())
        il.add_value('id', self.pid)

        goal_object = response.xpath('//*[@id="fund-project"]/ul/li[1]/div[2]/p[2]/text()').extract()
        if len(goal_object) is 0:
            il.add_value('goal', '')
        else:
            il.add_value('goal', str(goal_object))

        # TODO: nr. of backers
        pledged_object = response.xpath('//*[@id="fund-project"]/ul/li[1]/div[2]/h3/text()').extract()

        if len(pledged_object) is 0:
            pledged_object = response.xpath('//*[@id="fund-project"]/ul/li[1]/div/h3/text()').extract()
        else:
            pledged_object = 0

        il.add_value('pledged', str(pledged_object))

        return il.load_item()


