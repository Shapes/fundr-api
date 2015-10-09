# -*- coding: utf-8 -*-

__author__ = 'marko'

import scrapy
from scrapy.loader import ItemLoader

from cfservis.items import IndiegogoUpItem


class IndiegogoSpiderUpdater(scrapy.Spider):
    name = "indiegogo_updater"
    allowed_domains = ["indiegogo.com"]
    start_urls = [
        "https://www.indiegogo.com/projects/IME",
    ]
    project = ""
    pid = ""

    def __init__(self, pro=None, pid=None, *args, **kwargs):
        super(IndiegogoSpiderUpdater, self).__init__(*args, **kwargs)
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
            print "\n Error_ig_updater: Project ID is not defined!"

    def parse(self, response):
        il = ItemLoader(item=IndiegogoUpItem())
        il.add_value('id', self.pid)

        goal_object = response.xpath('//*[@id="i-contrib-box-rework"]/div[2]/span[2]/span/span/text()').extract()
        if len(goal_object) is not 0:
            il.add_value('goal', str(goal_object))
        else:
            il.add_value('goal', '')

        # TODO: nr. of backers
        pledged_object = response.xpath('//*[@id="i-contrib-box-rework"]/div[1]/div[1]/span/span/text()').extract()
        if len(pledged_object) is not 0:
            il.add_value('pledged', str(pledged_object))
        else:
            pledged = str(response.xpath('/html/body/div[8]/div/div[2]/div[2]/div[1]/div[1]/div[2]/span/span').extract())
            il.add_value('pledged', pledged)

        return il.load_item()


