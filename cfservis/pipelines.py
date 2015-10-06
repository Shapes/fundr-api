# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import sys
import MySQLdb
from peewee import *
from playhouse.db_url import connect
from datetime import datetime


db = connect(os.environ.get('DATABASE') or 'mysql://root:@127.0.0.1:3306/cfa')


class MySQLModel(Model):
    """A base model for my MySQL database"""
    class Meta:
        database = db


class App_Project(MySQLModel):
    second_id = CharField(max_length=256)
    title = CharField(max_length=256)
    author = CharField(max_length=256)
    project_url = CharField(max_length=256)
    img_url = CharField(max_length=256)
    location = CharField(max_length=256)
    end = CharField(max_length=256)
    pledged = IntegerField(default=0)
    goal = IntegerField()
    currency = CharField(max_length=5)
    date_modified = DateTimeField()
    active = IntegerField(default=0)
    website = IntegerField()
    type = IntegerField()
    category_id = IntegerField()


class MySQLStorePipeline(object):
    st_duplikatov = 0
    st_vnosov = 0

    def __init__(self):
        db.connect()

    def new_entry(self, item):
        try:
            projekt = App_Project.create(
                title=item['title'].encode('utf-8'),
                author=item['author'].encode('utf-8'),
                end=item['end'].encode('utf-8'),
                img_url=item['img_url'].encode('utf-8'),
                location=item['location'].encode('utf-8'),
                project_url=item['project_url'].encode('utf-8'),
                second_id=item['id'].encode('utf-8'),
                category_id=int(item['category_id']),
                pledged=int(item['pledged']),
                goal=int(0),
                date_modified=datetime.now(),
                type=item['type'],
                website=item['website'],
                currency=item['currency'],
            )
        except IntegrityError:
            print "Error in adding " + item['id']

    def update_entry(self, item):
        project = App_Project.get(App_Project.id == item['id'])
        project.pledged = item['pledged']
        project.goal = item['goal']
        project.date_modified = datetime.now()
        project.save()

    def update_entry_ig(self, item):
        project = App_Project.get(App_Project.title == item['title'])
        project.pledged = item['pledged']
        project.goal = item['goal']
        project.date_modified = datetime.now()
        project.save()

    def process_item(self, item, spider):
        tip_pajka = spider.name[-4:]

        if tip_pajka == "tter": #getting new projects

            if spider.name == 'indiegogo_getter':
                try:
                    data = App_Project.get(App_Project.title == str(item['title']))
                except App_Project.DoesNotExist:
                    data = None
            else:
                try:
                    data = App_Project.get(App_Project.second_id == str(item['id']))
                except App_Project.DoesNotExist:
                    data = None

            if data is not None:
                self.st_duplikatov += 1
            else:
                self.new_entry(item)
                self.st_vnosov += 1


            # statistics
            print ":>:Duplicates: " + str(self.st_duplikatov)
            print ":<:New projects: " + str(self.st_vnosov) + " \n"
        elif tip_pajka == "ater": #updating projects
            try:
                # TODO: Check date && compare pledged with goal -> active=0 or 1
                if spider.name == "indiegogo_updater":
                    self.update_entry_ig(item)
                    print "Project with title " + item['title'] + " updated."
                else:
                    self.update_entry(item)
                    print "Project with id " + str(item['id']) + " updated."
            except MySQLdb.Error, e:
                print "Error %s: %s" % (e.args[0], e.args[1])

        return item

