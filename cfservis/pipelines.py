# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from __future__ import print_function
import os
import re
import MySQLdb
from peewee import *
from playhouse.db_url import connect
from datetime import datetime
from colorama import Fore

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
    pledged = IntegerField()
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
            print("Error in adding " + item['id'])

    def update_entry(self, item):
        timestamp = datetime.now()
        project = App_Project.get(App_Project.id == item['id'])
        end_date = re.split('-', project.end)
        end = datetime(int(end_date[0]), int(end_date[1]), int(end_date[2]))

        if int(item['pledged']) > 0:
            project.pledged = item['pledged']
        try:
            project.goal = item['goal']
        except KeyError:
            print(Fore.RED + "No goal defined!" + Fore.WHITE)
        if project.pledged >= project.goal or end < timestamp:
            project.active = 0
            print(Fore.RED + "Funded or ended!" + Fore.WHITE)
        else:
            project.active = 1
        project.date_modified = timestamp
        project.save()

    def process_item(self, item, spider):
        tip_pajka = spider.name[-4:]

        if tip_pajka == "tter":  # getting new projects

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
            print(":>:Duplicates: " + str(self.st_duplikatov))
            print(":<:New projects: " + str(self.st_vnosov) + " \n")
        elif tip_pajka == "ater":  # updating projects
            self.update_entry(item)
            print(Fore.BLUE + "Project with id " + item['id'] + " updated." + Fore.WHITE)

        return item

