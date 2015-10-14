# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import Join, MapCompose, TakeFirst
from w3lib.html import remove_tags
import re
import datetime
from datetime import timedelta
from pycurrency import converter

categories = []
categories.append("art")
categories.append("comics")
categories.append("dance")
categories.append("design")
categories.append("fashion")
categories.append("music") # music & audio
categories.append("games")
categories.append("food")
categories.append("photography")
categories.append("film%20&%20video")
categories.append("technology")
categories.append("theater")
categories.append("publishing")
categories.append("crafts")
categories.append("unknown")

IG_CATEGORIES = {
    'animals': '15',
    'art': '1',
    'comics': '2',
    'community': '14',
    'dance': '3',
    'design': '4',
    'education': '13',
    'environment': '14',
    'fashion': '5',
    'film': '10',
    'food': '8',
    'gaming': '7',
    'health': '15',
    'music': '6',
    'photography': '9',
    'publicist': '13',
    'religion': '15',
    'small_business': '14',
    'sports': '15',
    'technology': '11',
    'theatre': '12',
    'video_web': '10',
    'writing': '13',
}


RH_CATEGORIES = {
    '1': '6',
    '2': '10',
    '3': '10',
    '4': '13',
    '5': '12',
    '6': '3',
    '7': '9',
    '8': '1',
    '9': '1',
    '10': '15',
    '11': '4',
    '12': '14',
    '13': '13',
    '14': '15',
    '15': '8',
    '17': '15',
    '18': '5',
    '19': '15',
    '20': '11',
    '21': '15',
    '22': '13',
    '23': '7',
    '24': '15',
    '25': '15',
    '26': '11',
    '27': '10',
    '28': '15',
    '30': '10',
    '35': '10',
    '36': '2',
    '37': '15',
    '38': '10',
    '41': '15',
    '100': '15'
}


def remove_shit(value):
    value = value.decode("utf-8").replace(u"[u'", "")
    value = value.replace(u"[u\"", "")
    value = value.replace("']", "")
    value = value.replace("\"]", "")
    return value


def parse_id(value):
    url = value.decode('utf-8')
    m = re.search('s/[a-z0-9A-Z-]+/', url)
    pid = (m.group(0)).replace("s/", "")
    pid = pid.replace("/", "")
    return pid


def parse_date_ks(value):
    value = value.decode("utf-8")
    year = value[:4]
    month = value[5:7]
    day = value[8:10]
    date = year + '-' + month + '-' + day
    return date


def remove_chars(string):
    string = string.decode('utf-8')
    string = string.strip()
    niz = ''.join(i for i in string if i.isdigit())
    return niz


def parse_date(days):
    days = remove_chars(days)
    date_now = datetime.datetime.now()
    end_date = date_now + timedelta(int(days))
    return str(end_date.date())  # LETO-MESEC-DAN


def parse_author(value):
    value = value.decode('utf-8')
    return value[3:]


def parse_url_k(value):
    value = value.decode('utf-8')
    value = "https://www.kickstarter.com" + value
    return value[:-20]


def parse_ks_category(category):
    if category == 'journalism':
        return 13
    else:
        try:
            index = categories.index(category)+1
        except NameError:
            return 15
        else:
            return index


def parse_ig_category(category):
    return IG_CATEGORIES[category]


def parse_rh_category(category):
    return RH_CATEGORIES[category]


def parse_money_ks(value):
    if value is '':
        return value
    kes = value.decode('unicode-escape')
    value = ''.join(i for i in kes if i.isdigit())
    return value


def parse_money_ig(value):
    kes = value.decode('unicode-escape')
    value = ''.join(i for i in kes if i.isdigit())
    return value


def parse_money(value):
    value = ''.join(i for i in value if i.isdigit())
    return value


def parse_currency(value):
    currency = (value.split()[1]).upper()
    return currency


class KickstarterItem(scrapy.Item):
    id = scrapy.Field(
        input_processor=MapCompose(parse_id),
        output_processor=TakeFirst()
    )
    title = scrapy.Field(
        input_processor=MapCompose(remove_shit),
        output_processor=TakeFirst()
    )
    author = scrapy.Field(
        input_processor=MapCompose(remove_shit),
        output_processor=TakeFirst()
    )
    project_url = scrapy.Field(
        input_processor=MapCompose(remove_shit, parse_url_k),
        output_processor=TakeFirst()
    )
    img_url = scrapy.Field(
        input_processor=MapCompose(remove_shit),
        output_processor=TakeFirst()
    )
    location = scrapy.Field(
        input_processor=MapCompose(remove_shit),
        output_processor=TakeFirst()
    )
    end = scrapy.Field(
        input_processor=MapCompose(remove_shit, parse_date_ks),
        output_processor=TakeFirst()
    )
    category_id = scrapy.Field(
        input_processor=MapCompose(parse_ks_category),
        output_processor=TakeFirst()
    )
    pledged = scrapy.Field(
        input_processor=MapCompose(remove_shit, parse_money_ks),
        output_processor=TakeFirst()
    )
    currency = scrapy.Field(
        input_processor=MapCompose(remove_shit, parse_currency),
        output_processor=TakeFirst()
    )
    goal = scrapy.Field(
        input_processor=MapCompose(remove_shit),
        output_processor=TakeFirst()
    )
    website = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )
    type = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )


class IndiegogoItem(scrapy.Item):
    id = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )
    title = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )
    author = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )
    project_url = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )
    img_url = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )
    location = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=Join()
    )
    end = scrapy.Field(
        input_processor=MapCompose(parse_date),
        output_processor=TakeFirst()
    )
    category_id = scrapy.Field(
        input_processor=MapCompose(parse_ig_category),
        output_processor=TakeFirst()
    )
    pledged = scrapy.Field(
        input_processor=MapCompose(parse_money),
        output_processor=TakeFirst()
    )
    currency = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )
    goal = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )
    website = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )
    type = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )


class RockethubItem(scrapy.Item):
    id = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )
    title = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )
    author = scrapy.Field(
        input_processor=MapCompose(parse_author),
        output_processor=TakeFirst()
    )
    project_url = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )
    img_url = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )
    location = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=Join()
    )
    end = scrapy.Field(
        input_processor=MapCompose(parse_date),
        output_processor=TakeFirst()
    )
    category_id = scrapy.Field(
        input_processor=MapCompose(parse_rh_category),
        output_processor=TakeFirst()
    )
    pledged = scrapy.Field(
        input_processor=MapCompose(parse_money),
        output_processor=TakeFirst()
    )
    currency = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )
    goal = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )
    website = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )
    type = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )


class KickstarterUpItem(scrapy.Item):
    id = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )
    pledged = scrapy.Field(
        input_processor=MapCompose(parse_money_ks),
        output_processor=TakeFirst()
    )
    goal = scrapy.Field(
        input_processor=MapCompose(parse_money_ks),
        output_processor=TakeFirst()
    )


class IndiegogoUpItem(scrapy.Item):
    id = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )
    pledged = scrapy.Field(
        input_processor=MapCompose(parse_money_ig),
        output_processor=TakeFirst()
    )
    goal = scrapy.Field(
        input_processor=MapCompose(parse_money_ig),
        output_processor=TakeFirst()
    )

class RockethubUpItem(scrapy.Item):
    id = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )
    pledged = scrapy.Field(
        input_processor=MapCompose(parse_money_ig),
        output_processor=TakeFirst()
    )
    goal = scrapy.Field(
        input_processor=MapCompose(parse_money_ig),
        output_processor=TakeFirst()
    )
