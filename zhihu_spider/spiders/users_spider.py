# -*- coding: utf-8 -*-
import logging
import os
import time

import scrapy

from zhihu_spider.items import UserItem, AnswerItem, FollowingItem
from zhihu_spider.myconfig import UsersConfig  # 爬虫配置

logging.basicConfig(filename='links.log', level=logging.INFO)


def findUsername(url):
    urlParts = url.split('/')
    indexOfPeople = urlParts.index('people')
    return urlParts[indexOfPeople + 1]


class UsersSpider(scrapy.Spider):
    name = 'users'
    domain = 'https://www.zhihu.com'
    login_url = 'https://www.zhihu.com/login/email'
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Connection": "keep-alive",
        "Host": "www.zhihu.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36"
    }

    def __init__(self, user=None):
        self.user_url = 'https://www.zhihu.com/people/{0}'.format(user)

    def start_requests(self):
        # yield scrapy.Request(
        #     url=self.domain,
        #     headers=self.headers,
        #     meta={
        #         'proxy': UsersConfig['proxy'],
        #         'cookiejar': 1
        #     },
        #     callback=self.request_captcha
        # )
        yield scrapy.Request(
            url=self.user_url,
            headers=self.headers,
            meta={
                'proxy': UsersConfig['proxy'],
                'cookiejar': 1
            },
            callback=self.request_zhihu
        )

    def request_captcha(self, response):
        # 获取_xsrf值
        _xsrf = response.css('input[name="_xsrf"]::attr(value)').extract()[0]
        # 获取验证码地址
        captcha_url = 'http://www.zhihu.com/captcha.gif?r=' + str(time.time() * 1000)
        # 准备下载验证码
        yield scrapy.Request(
            url=captcha_url,
            headers=self.headers,
            meta={
                'proxy': UsersConfig['proxy'],
                'cookiejar': response.meta['cookiejar'],
                '_xsrf': _xsrf
            },
            callback=self.download_captcha
        )

    def download_captcha(self, response):
        # 下载验证码
        with open('captcha.gif', 'wb') as fp:
            fp.write(response.body)
        # 用软件打开验证码图片
        os.system('start captcha.gif')
        # 输入验证码
        print('Please enter captcha: ')
        captcha = input()

        yield scrapy.FormRequest(
            url=self.login_url,
            headers=self.headers,
            formdata={
                'email': UsersConfig['email'],
                'password': UsersConfig['password'],
                '_xsrf': response.meta['_xsrf'],
                'remember_me': 'true',
                'captcha': captcha
            },
            meta={
                'proxy': UsersConfig['proxy'],
                'cookiejar': response.meta['cookiejar']
            },
            callback=self.request_zhihu
        )

    def request_zhihu(self, response):
        # yield scrapy.Request(
        #     url=self.user_url + '/activities',
        #     headers=self.headers,
        #     meta={
        #         'proxy': UsersConfig['proxy'],
        #         'cookiejar': response.meta['cookiejar'],
        #         'from': {
        #             'sign': 'else',
        #             'data': {}
        #         },
        #         'PhantomJS': True
        #     },
        #     callback=self.user_item,
        #     dont_filter=True
        # )

        yield scrapy.Request(
            url=self.user_url + '/following',
            headers=self.headers,
            meta={
                'proxy': UsersConfig['proxy'],
                'cookiejar': response.meta['cookiejar'],
                'from': {
                    'sign': 'else',
                    'data': {}
                },
                'PhantomJS': True
            },
            callback=self.user_start,
            dont_filter=True
        )

        # yield scrapy.Request(
        #     url=self.user_url + '/followers',
        #     headers=self.headers,
        #     meta={
        #         'proxy': UsersConfig['proxy'],
        #         'cookiejar': response.meta['cookiejar'],
        #         'from': {
        #             'sign': 'else',
        #             'data': {}
        #         }
        #     },
        #     callback=self.user_start,
        #     dont_filter=True
        # )

    def user_start(self, response):
        # 获取个人信息
        item = UserItem()
        item['type'] = 'user'

        # 用户名
        urlParts = response.url.split('/')
        indexOfPeople = urlParts.index('people')
        item['uid'] = urlParts[indexOfPeople + 1]

        # 姓名
        item['name'] = response.xpath('//span[@class="ProfileHeader-name"]/text()')[0].extract()

        # 头像
        item['avatar'] = response.xpath('//div[@class="UserAvatar ProfileHeader-avatar"]/img/@src')[0].extract()

        # 简介
        try:
            item['motto'] = response.xpath('//span[@class="RichText ProfileHeader-headline"]/text()')[0].extract()
        except:
            item['motto'] = ''

        # 赞同数
        try:
            item['agree'] = int(
                response.xpath('//svg[@class="Icon IconGraf-icon Icon--like"]/../../text()[2]')[0].extract())
        except:
            item['agree'] = 0

        # 详细信息部分
        profileItems = response.xpath('//div[@class="ProfileHeader-detail"]//div[@class="ProfileHeader-detailItem"]')
        for profileItem in profileItems:
            lable = profileItem.xpath('./span[@class="ProfileHeader-detailLabel"]/text()')[0].extract()
            if lable == '居住地':
                item['location'] = ''.join(
                    profileItem.xpath('./div[@class="ProfileHeader-detailValue"]/span/text()').extract())
            elif lable == '所在行业':
                item['business'] = profileItem.xpath('./div[@class="ProfileHeader-detailValue"]/text()')[0].extract()
            elif lable == '职业经历':
                item['company'] = ''.join(profileItem.xpath(
                    './div[@class="ProfileHeader-detailValue"]/div[@class="ProfileHeader-field"]/text()').extract())
            elif lable == '教育经历':
                item['education'] = ''.join(profileItem.xpath(
                    './div[@class="ProfileHeader-detailValue"]/div[@class="ProfileHeader-field"]/text()').extract())
            elif lable == '个人简介':
                item['content'] = ''.join(
                    profileItem.xpath('./div[@class="RichText ProfileHeader-detailValue"]/text()').extract())

        yield item

        # 获取关注的人的信息
        # 获取关注页数
        try:
            totalPageNum = int(
                response.xpath('//button[@class="Button PaginationButton Button--plain"][last()]/text()'))
        except:
            totalPageNum = 1

        for i in range(1, totalPageNum + 1):
            yield scrapy.Request(
                url='{0}?page={1}'.format(response.url, i),
                headers=self.headers,
                meta={
                    'proxy': UsersConfig['proxy'],
                    'cookiejar': response.meta['cookiejar'],
                    'from': {
                        'sign': 'else',
                        'data': {}
                    },
                    'PhantomJS': True
                },
                callback=self.parse_following,
                dont_filter=True
            )

    def parse_following(self, response):
        # 获取当前用户名称
        username = findUsername(response.url)

        # 获取本页的关注的人的地址
        url_list = response.xpath('//div[@class="ContentItem-head"]//a[@class="UserLink-link"]/@href')

        # 本页人数少于10，忽略
        if len(url_list) < 10:
            return

        print('在{0}发现了以下链接'.format(response.url))
        urls = [url.extract() for url in url_list]
        print(urls)
        for url in urls:
            if '/people' in url:
                item = FollowingItem()
                item['type'] = 'following'
                item['uid'] = findUsername(url)
                item['followed_by'] = username
                yield item

                # yield scrapy.Request(
                #     url='https://www.zhihu.com{0}/activities'.format(url),
                #     headers=self.headers,
                #     meta={
                #         'proxy': UsersConfig['proxy'],
                #         'cookiejar': response.meta['cookiejar'],
                #         'from': {
                #             'sign': 'else',
                #             'data': {}
                #         },
                #         'PhantomJS': True
                #     },
                #     callback=self.user_item,
                #     dont_filter=True
                # )

                yield scrapy.Request(
                    url='https://www.zhihu.com{0}/following'.format(url),
                    headers=self.headers,
                    meta={
                        'proxy': UsersConfig['proxy'],
                        'cookiejar': response.meta['cookiejar'],
                        'from': {
                            'sign': 'else',
                            'data': {}
                        },
                        'PhantomJS': True
                    },
                    callback=self.user_start,
                    dont_filter=True
                )
                # sel_root = response.xpath('//div[@class="ContentItem-head"]')
                # print(response.url)
                # print(sel_root)
                # print(len(sel_root))
                # print(response.xpath('//button[@class="Button PaginationButton Button--plain"][last()]/text()'))
                # # page_num = response.xpath('//button[@class="Button PaginationButton Button--plain"][last()]/text()')[0].extract()
                # # 判断关注列表是否为空
                # if len(sel_root):
                #     for sel in sel_root:
                #         print(sel.xpath('//a/@href')[0].extract())
                #         people_url = 'https://www.zhihu.com' + sel.xpath('//a/@href')[0].extract()
                #         print(people_url)
                #         yield scrapy.Request(
                #             url=people_url + '/activities',
                #             headers=self.headers,
                #             meta={
                #                 'proxy': UsersConfig['proxy'],
                #                 'cookiejar': response.meta['cookiejar'],
                #                 'from': {
                #                     'sign': 'else',
                #                     'data': {}
                #                 }
                #             },
                #             callback=self.user_item,
                #             dont_filter=True
                #         )
                #
                #         yield scrapy.Request(
                #             url=people_url + '/following',
                #             headers=self.headers,
                #             meta={
                #                 'proxy': UsersConfig['proxy'],
                #                 'cookiejar': response.meta['cookiejar'],
                #                 'from': {
                #                     'sign': 'else',
                #                     'data': {}
                #                 }
                #             },
                #             callback=self.user_start,
                #             dont_filter=True
                #         )
                #
                #         # yield scrapy.Request(
                #         #     url=people_url + '/followers',
                #         #     headers=self.headers,
                #         #     meta={
                #         #         'proxy': UsersConfig['proxy'],
                #         #         'cookiejar': response.meta['cookiejar'],
                #         #         'from': {
                #         #             'sign': 'else',
                #         #             'data': {}
                #         #         }
                #         #     },
                #         #     callback=self.user_start,
                #         #     dont_filter=True
                #         # )

    # def user_item(self, response):
    #
    #     item = UserItem()
    #     item['type'] = 'user'
    #
    #     # 用户名
    #     urlParts = response.url.split('/')
    #     indexOfPeople = urlParts.index('people')
    #     item['uid'] = urlParts[indexOfPeople + 1]
    #
    #     # 姓名
    #     item['name'] = response.xpath('//span[@class="ProfileHeader-name"]/text()')[0].extract()
    #
    #     # 头像
    #     item['avatar'] = response.xpath('//div[@class="UserAvatar ProfileHeader-avatar"]/img/@src')[0].extract()
    #
    #     # 简介
    #     try:
    #         item['motto'] = response.xpath('//span[@class="RichText ProfileHeader-headline"]/text()')[0].extract()
    #     except:
    #         item['motto'] = ''
    #
    #     # 赞同数
    #     try:
    #         item['agree'] = int(
    #             response.xpath('//svg[@class="Icon IconGraf-icon Icon--like"]/../../text()[2]')[0].extract())
    #     except:
    #         item['agree'] = 0
    #
    #     # 详细信息部分
    #     profileItems = response.xpath('//div[@class="ProfileHeader-detail"]//div[@class="ProfileHeader-detailItem"]')
    #     for profileItem in profileItems:
    #         lable = profileItem.xpath('./span[@class="ProfileHeader-detailLabel"]/text()')[0].extract()
    #         if lable == '居住地':
    #             item['location'] = ''.join(
    #                 profileItem.xpath('./div[@class="ProfileHeader-detailValue"]/span/text()').extract())
    #         elif lable == '所在行业':
    #             item['business'] = profileItem.xpath('./div[@class="ProfileHeader-detailValue"]/text()')[0].extract()
    #         elif lable == '职业经历':
    #             item['company'] = ''.join(profileItem.xpath(
    #                 './div[@class="ProfileHeader-detailValue"]/div[@class="ProfileHeader-field"]/text()').extract())
    #         elif lable == '教育经历':
    #             item['education'] = ''.join(profileItem.xpath(
    #                 './div[@class="ProfileHeader-detailValue"]/div[@class="ProfileHeader-field"]/text()').extract())
    #         elif lable == '个人简介':
    #             item['content'] = ''.join(
    #                 profileItem.xpath('./div[@class="RichText ProfileHeader-detailValue"]/text()').extract())
    #
    #     yield item


class AnswerSpider(scrapy.Spider):
    name = 'answers'
    domain = 'https://www.zhihu.com'
    login_url = 'https://www.zhihu.com/login/email'
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Connection": "keep-alive",
        "Host": "www.zhihu.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36"
    }

    def __init__(self, user=None):
        self.user_url = 'https://www.zhihu.com/people/{0}'.format(user)

    def start_requests(self):
        yield scrapy.Request(
            url=self.domain,
            headers=self.headers,
            meta={
                'proxy': UsersConfig['proxy'],
                'cookiejar': 1
            },
            callback=self.request_captcha
        )

    def request_captcha(self, response):
        # 获取_xsrf值
        _xsrf = response.css('input[name="_xsrf"]::attr(value)').extract()[0]
        # 获取验证码地址
        captcha_url = 'http://www.zhihu.com/captcha.gif?r=' + str(time.time() * 1000)
        # 准备下载验证码
        yield scrapy.Request(
            url=captcha_url,
            headers=self.headers,
            meta={
                'proxy': UsersConfig['proxy'],
                'cookiejar': response.meta['cookiejar'],
                '_xsrf': _xsrf
            },
            callback=self.download_captcha
        )

    def download_captcha(self, response):
        # 下载验证码
        with open('captcha.gif', 'wb') as fp:
            fp.write(response.body)
        # 用软件打开验证码图片
        os.system('start captcha.gif')
        # 输入验证码
        print('Please enter captcha: ')
        captcha = input()

        yield scrapy.FormRequest(
            url=self.login_url,
            headers=self.headers,
            formdata={
                'email': UsersConfig['email'],
                'password': UsersConfig['password'],
                '_xsrf': response.meta['_xsrf'],
                'remember_me': 'true',
                'captcha': captcha
            },
            meta={
                'proxy': UsersConfig['proxy'],
                'cookiejar': response.meta['cookiejar']
            },
            callback=self.request_zhihu
        )

    def request_zhihu(self, response):
        yield scrapy.Request(
            url='{0}/answers'.format(self.user_url),
            headers=self.headers,
            meta={
                'proxy': UsersConfig['proxy'],
                'cookiejar': response.meta['cookiejar'],
                'from': {
                    'sign': 'else',
                    'data': {}
                },
                'PhantomJS': True
            },
            callback=self.request_answer,
            dont_filter=True
        )

    def request_answer(self, response):

        total_page = response.xpath('//button[@class="Button PaginationButton Button--plain"][last()]/text()').extract()
        end = total_page if total_page <= 20 else 20
        for i in range(1, end + 1):
            yield scrapy.Request(
                url='{0}/answers?page={1}'.format(self.user_url, i),
                headers=self.headers,
                meta={
                    'proxy': UsersConfig['proxy'],
                    'cookiejar': response.meta['cookiejar'],
                    'from': {
                        'sign': 'else',
                        'data': {}
                    },
                    'PhantomJS': True
                },
                callback=self.answer_start,
                dont_filter=True
            )

    def answer_start(self, response):

        url_list = response.xpath('//h2[@class="ContentItem-title"]/a/@href')
        logging.info('在{0}发现了以下链接:'.format(response.url))
        urls = [url.extract() for url in url_list]
        for url in urls:
            logging.info(url)
            if '/answer' in url:
                yield scrapy.Request(
                    url='https://www.zhihu.com' + url,
                    headers=self.headers,
                    meta={
                        'proxy': UsersConfig['proxy'],
                        'cookiejar': response.meta['cookiejar'],
                        'from': {
                            'sign': 'else',
                            'data': {}
                        }
                    },
                    callback=self.answer_item,
                    dont_filter=True
                )

    def answer_item(self, response):
        item = AnswerItem()

        # url
        item['url'] = response.url

        # 标题
        try:
            item['title'] = response.xpath('//h1[@class="QuestionHeader-title"]/text()')[0].extract()
        except:
            item['title'] = ''

        # 详细
        try:
            item['detail'] = response.xpath('//div[@class="QuestionHeader-detail"]//span/text()')[0].extract()
        except:
            item['detail'] = ''

        # 内容
        try:
            result = response.xpath(
                '//div[@class="QuestionAnswer-content"]//span[@class="RichText CopyrightRichText-richText"]')
            info = result.xpath('string(.)')[0].extract()

            item['content'] = info
        except:
            item['content'] = ''

        # 赞
        try:
            item['upvote_num'] = response.xpath(
                '//div[@class="ContentItem-actions"]//button[@class="VoteButton VoteButton--up"]/text()')[0].extract()
        except:
            item['upvote_num'] = ''

        # 时间
        try:
            item['timestamp'] = response.xpath('//div[@class="ContentItem-time"]/a/span/@data-tooltip')[0].extract()
        except:
            item['timestamp'] = ''

        # user_name
        item['user_name'] = \
            response.xpath('//div[@class="QuestionAnswer-content"]//a[@class="UserLink-link"]/@href')[
                0].extract().split(
                '/')[2]

        yield item
