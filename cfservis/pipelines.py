# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sys
import MySQLdb
from peewee import *
import hashlib
from scrapy.exceptions import DropItem
from scrapy.http import Request
from datetime import datetime


class MySQLStorePipeline(object):
    st_duplikatov = 0
    st_vnosov = 0

    def __init__(self):
        self.conn = MySQLdb.connect(user='root', passwd='', db='cfa', host='127.0.0.1', charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def new_entry(self, item):
        self.cursor.execute("""INSERT INTO app_project
 (title, author, end, img_url, location, project_url, second_id, category_id, pledged, goal, date_modified, type, website, currency)
                                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                                                                        (item['title'].encode('utf-8'),
                                                                                         item['author'].encode('utf-8'),
                                                                                         item['end'].encode('utf-8'),
                                                                                         item['img_url'].encode('utf-8'),
                                                                                         item['location'].encode('utf-8'),
                                                                                         item['project_url'].encode('utf-8'),
                                                                                         item['id'].encode('utf-8'),
                                                                                         int(item['category_id']),
                                                                                         int(item['pledged']),
                                                                                         int(0),
                                                                                         datetime.now(),
                                                                                         item['type'],
                                                                                         item['website'],
                                                                                         item['currency']))

    def update_entry(self, item):
        self.cursor.execute("""UPDATE app_project
                               SET pledged=%s, goal=%s, date_modified=%s WHERE id=%s""", (item['pledged'],
                                                                                           item['goal'],
                                                                                           datetime.now(),

                                                                                           item['id']))
    def update_entry_ig(self, item):
        self.cursor.execute("""UPDATE app_project
                               SET pledged=%s, goal=%s, date_modified=%s WHERE title=%s""", (item['pledged'],
                                                                                           item['goal'],
                                                                                           datetime.now(),
                                                                                           item['title']))
    def process_item(self, item, spider):
        tip_pajka = spider.name[-4:]

        if tip_pajka == "tter": #getting new projects
            try:
                if spider.name == 'indiegogo_getter':
                    ide = str(item['title'])
                    query = ("SELECT * FROM app_project WHERE title=%s")
                else:
                    ide = str(item['id'])
                    query = ("SELECT * FROM app_project WHERE second_id=%s")

                self.cursor.execute(query, (ide,))
                data = self.cursor.fetchone()

                if data is not None:
                    self.st_duplikatov += 1
                else:
                    try:
                        self.new_entry(item)
                        self.conn.commit()
                        self.st_vnosov += 1
                    except MySQLdb.Error, e:
                        print "Error %s: %s" % (e.args[0], e.args[1])
            except MySQLdb.Error, e:
                print "Error %s" % (e.args[0])
                    # statistics
            print ":>:Duplicates: " + str(self.st_duplikatov)
            print ":<:New projects: " + str(self.st_vnosov) + " \n"
        elif tip_pajka == "ater": #updating projects
            try:
                # TODO: Check date && compare pledged with goal -> active=0 or 1
                if spider.name == "indiegogo_updater":
                    self.update_entry_ig(item)
                    self.conn.commit()
                    print "Project with title " + item['title'] + " updated."
                else:
                    self.update_entry(item)
                    self.conn.commit()
                    print "Project with id " + str(item['id']) + " updated."
            except MySQLdb.Error, e:
                print "Error %s: %s" % (e.args[0], e.args[1])

        return item

