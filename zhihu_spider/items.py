# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class UserItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    name = scrapy.Field()
    content = scrapy.Field()
    business = scrapy.Field()
    company = scrapy.Field()
    position = scrapy.Field()
    education = scrapy.Field()
    major = scrapy.Field()
    gender = scrapy.Field()
    avatar = scrapy.Field()
    agree = scrapy.Field()
    thanks = scrapy.Field()


class AnswerItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    detail = scrapy.Field()
    content = scrapy.Field()
    upvote_num = scrapy.Field()
    timestamp = scrapy.Field()
    user_name = scrapy.Field()