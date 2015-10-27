# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from __future__ import print_function
import os
import re
from peewee import *
from playhouse.db_url import connect
from datetime import datetime
from colorama import Fore

# db = connect(os.environ.get('DATABASE') or 'mysql://crawlers:@127.0.0.1:3306/cfa')
db = connect(os.environ.get('DATABASE') or 'postgres://cwbgprmyqmdquj:a8bxzQVPkh51SUnKIILPn-kn1H@ec2-'
                                           '54-197-241-24.compute-1.amazonaws.com:5432/d5rusc757iti8l')


class MySQLModel(Model):
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
    active = IntegerField(default=1)
    website = IntegerField()
    type = IntegerField()
    category_id = IntegerField()


class App_Erorrs(MySQLModel):
    message = CharField(max_length=400)
    date_modified = DateTimeField()


class MySQLStorePipeline(object):
    st_duplikatov = 0
    st_vnosov = 0

    def __init__(self):
        db.connect()
        pass

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
            try:
                err = App_Erorrs.create(message="Error in adding " + item['id'], date_modified=datetime.now())
            except Exception as e:
                print("Error adding an error !" + e.message)
        #db.close()

    def update_entry(self, item):
        timestamp = datetime.now()
        project = App_Project.get(App_Project.id == item['id'])
        end_date = re.split('-', project.end)
        end = datetime(int(end_date[0]), int(end_date[1]), int(end_date[2]))

        # set pledged
        try:
            pledged = item['pledged']
            if int(pledged) > 0:
                project.pledged = int(pledged)
        except Exception as e:
            print(Fore.RED + "Can't retrieve pledged!" + " Because: " + e.message + Fore.WHITE)

        # set goal
        try:
            project.goal = item['goal']
        except KeyError:
            print(Fore.RED + "Can't retrieve goal!" + Fore.WHITE)

        # check if project ended or is funded = LIFECycle
        if project.pledged >= project.goal or end < timestamp:
            project.active = 0
            print(Fore.RED + "Funded or ended!" + Fore.WHITE)
        else:
            project.active = 1

        # save update
        try:
            project.date_modified = timestamp
            project.save()
        except Exception as e:
            print(Fore.RED + "Error saving project with id " + str(item['id']) + ". Because: " + e.message + Fore.WHITE)
            try:
                err = App_Erorrs.create(message="Error saving project with id " + str(item['id']), date_modified=timestamp)
            except Exception as e:
                print("Error adding an error !" + e.message)
        db.close()

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

