# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import logging
import os

import time
from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver

from zhihu_spider.myconfig import PhantomJSConfig, ImageConfig


class ZhihuSpiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class PhantomJSMiddleware(object):
    @classmethod
    def process_request(cls, request, spider):
        # 睡1s等待页面加载完毕
        time.sleep(1)
        if 'PhantomJS' in request.meta:
            driver = webdriver.PhantomJS(
                executable_path=PhantomJSConfig['path'])
            driver.set_window_size(1200, 900)
            driver.get(request.url)

            # 点击“查看详细资料”按钮
            try:
                more_profile = driver.find_element_by_xpath(
                    '//button[@class="Button ProfileHeader-expandButton Button--plain"]')
                more_profile.click()
                # 睡1s等待文字加载
                time.sleep(1)
            except:
                pass


            content = driver.page_source.encode('utf-8')

            # # 保存当前页面截图
            # urlParts = request.url.split('/')
            # indexOfPeople = urlParts.index('people')
            # image_folder = ImageConfig['path']
            # image_name = os.path.join(image_folder, '{0}_{1}.png'.format(urlParts[indexOfPeople + 1], urlParts[-1]))
            #
            # # 不存在则创建截图
            # if not os.path.isfile(image_name):
            #     print('Save page to image: {0}'.format(image_name))
            #     driver.save_screenshot(image_name)

            driver.quit()
            return HtmlResponse(request.url, encoding='utf-8', body=content, request=request)
