# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class UserItem(scrapy.Item):
    # define the fields for your item here like:
    uid = scrapy.Field()            # 用户名
    name = scrapy.Field()           # 昵称
    motto = scrapy.Field()          # 签名
    location = scrapy.Field()       # 居住地
    business = scrapy.Field()       # 行业
    company = scrapy.Field()        # 职业信息
    education = scrapy.Field()      # 教育信息
    content = scrapy.Field()        # 个人简介
    avatar = scrapy.Field()         # 头像
    agree = scrapy.Field()          # 赞同
    type = scrapy.Field()           # item类型


class AnswerItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    detail = scrapy.Field()
    content = scrapy.Field()
    upvote_num = scrapy.Field()
    timestamp = scrapy.Field()
    user_name = scrapy.Field()

class FollowingItem(scrapy.Item):
    uid = scrapy.Field()            # 用户名
    followed_by = scrapy.Field()    # 被某人关注
    type = scrapy.Field()           # item类型