# -*- coding: utf-8 -*-
import scrapy
import os
import time
from zhihu_spider.items import UserItem, AnswerItem
from zhihu_spider.myconfig import UsersConfig  # 爬虫配置


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

    def __init__(self, url=None):
        self.user_url = url

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
            url=self.user_url + '/activities',
            headers=self.headers,
            meta={
                'proxy': UsersConfig['proxy'],
                'cookiejar': response.meta['cookiejar'],
                'from': {
                    'sign': 'else',
                    'data': {}
                }
            },
            callback=self.user_item,
            dont_filter=True
        )

        yield scrapy.Request(
            url=self.user_url + '/following',
            headers=self.headers,
            meta={
                'proxy': UsersConfig['proxy'],
                'cookiejar': response.meta['cookiejar'],
                'from': {
                    'sign': 'else',
                    'data': {}
                }
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
        url_list = response.xpath('//div[@class="ContentItem-head"]//a/@href')
        print('在{0}发现了以下链接'.format(response.url))
        urls = [url.extract() for url in url_list]
        print(urls)
        for url in url_list:
            if '/people' in url.extract():
                yield scrapy.Request(
                    url='https://www.zhihu.com' + url.extract() + '/activities',
                    headers=self.headers,
                    meta={
                        'proxy': UsersConfig['proxy'],
                        'cookiejar': response.meta['cookiejar'],
                        'from': {
                            'sign': 'else',
                            'data': {}
                        }
                    },
                    callback=self.user_item,
                    dont_filter=True
                )

                yield scrapy.Request(
                    url='https://www.zhihu.com' + url.extract() + '/following',
                    headers=self.headers,
                    meta={
                        'proxy': UsersConfig['proxy'],
                        'cookiejar': response.meta['cookiejar'],
                        'from': {
                            'sign': 'else',
                            'data': {}
                        }
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

    def user_item(self, response):
        # def value(list):
        #     return list[0] if len(list) else ''
        # sel = response.xpath('//div[@class="zm-profile-header ProfileCard"]')
        # response_str = response.text.encode('utf-8')
        print('开始一波疯狂输出')
        item = UserItem()
        # url
        item['url'] = response.url
        # 姓名
        item['name'] = response.xpath('//span[@class="ProfileHeader-name"]/text()')[0].extract()
        # 简介
        try:
            item['content'] = response.xpath('//span[@class="RichText ProfileHeader-headline"]/text()')[0].extract()
        except:
            item['content'] = ''
            # 行业
        try:
            item['business'] = response.xpath('//div[@class="ProfileHeader-infoItem"][1]/text()[1]')[0].extract()
        except:
            item['business'] = ''
        # 公司
        try:
            item['company'] = response.xpath('//div[@class="ProfileHeader-infoItem"][1]/text()[2]')[0].extract()
        except:
            item['company'] = ''
        # 职位
        try:
            item['position'] = response.xpath('//div[@class="ProfileHeader-infoItem"][1]/text()[3]')[0].extract()
        except:
            item['position'] = ''
        # 学校
        try:
            item['education'] = response.xpath('//div[@class="ProfileHeader-infoItem"][2]/text()[1]')[0].extract()
        except:
            item['education'] = ''
        # 专业
        try:
            item['major'] = response.xpath('//div[@class="ProfileHeader-infoItem"][2]/text()[2]')[0].extract()
        except:
            item['major'] = ''
        # 性别,还有些问题
        try:
            item['gender'] = 0 if response.xpath('//svg[contains(@class, "Icon Icon--female")]') else 1
        except:
            item['gender'] = 1
        # 头像
        if len(response.xpath('//div[@class="UserAvatar ProfileHeader-avatar"]/img/@src')):
            item['avatar'] = response.xpath('//div[@class="UserAvatar ProfileHeader-avatar"]/img/@src')[0].extract()
        # 赞同
        try:
            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            print(response.xpath('//div[@class="IconGraf"]/text()[2]')[0].extract())
            item['agree'] = int(response.xpath('//div[@class="IconGraf"]/text()[2]')[0].extract())
        except:
            item['agree'] = 0
        # 感谢
        try:
            item['thanks'] = int(
                response.xpath('//div[@class="Profile-sideColumnItemValue"]/text()[1]')[0].extract().split(' ')[1])
        except:
            item['thanks'] = 0
        print('打印用户信息')
        print(item)
        yield item


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

    def __init__(self, url=None):
        self.user_url = url

    def start_requests(self):
        # if os.path.isfile('cookiejar'):
        #     with open('cookiejar', 'r') as f:
        #         cookiejar = f.read()
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
            url=self.user_url + '/answers',
            headers=self.headers,
            meta={
                'proxy': UsersConfig['proxy'],
                'cookiejar': response.meta['cookiejar'],
                'from': {
                    'sign': 'else',
                    'data': {}
                }
            },
            callback=self.answer_start,
            dont_filter=True
        )

    def answer_start(self, response):
        with open('response.txt', 'w',encoding='utf-8') as f:
            f.write(response.text)
        print(response)
        total_page = response.xpath('//button[@class="Button PaginationButton Button--plain"][last()]/text()')
        url_list = response.xpath('//h2[@class="ContentItem-title"]/a/@href')
        print('在{0}发现了以下链接:'.format(response.url))
        print(len(url_list))
        print(url_list)
        urls = [url.extract() for url in url_list]
        print(urls)
        for url in urls:
            print(url)
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
        print('开始一波疯狂输出')
        item = AnswerItem()
        # url
        item['url'] = response.url
        # 标题
        item['title'] = response.xpath('//h1[@class="QuestionHeader-title"]/text()')[0].extract()
        # 详细
        item['detail'] = response.xpath('//div[@class="QuestionHeader-detail"]//span/text()')[0].extract()
        # 内容
        results = response.xpath(
            '//div[@class="QuestionAnswer-content"]//span[@class="RichText CopyrightRichText-richText"]/text()').extract()
        info_list = ''
        print(results)
        print(len(results))
        for result in results:
            info_list += result

        item['content'] = info_list
        # 赞
        item['upvote_num'] = response.xpath(
            '//div[@class="ContentItem-actions"]//button[@class="VoteButton VoteButton--up"]/text()')[0].extract()
        # 时间
        item['timestamp'] = response.xpath('//div[@class="ContentItem-time"]/a/span/@data-tooltip')[0].extract()

        print('打印答案信息')
        print(item)
        yield item
