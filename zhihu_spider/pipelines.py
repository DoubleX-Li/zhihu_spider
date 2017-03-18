# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from zhihu_spider.models import Base, User, Answer


# class ZhihuSpiderPipeline(object):
#     def process_item(self, item, spider):
#         return item

class UserPipeline(object):
    def __init__(self):
        engine = create_engine('sqlite:///test.db')
        Base.metadata.create_all(engine)
        SessionCls = sessionmaker(bind=engine)
        self.session = SessionCls()

    def process_item(self, item, spider):
        temp = self.session.query(User).filter(User.url == item['url']).first()
        if temp:
            pass
        else:
            try:
                user = User(
                    item['url'],
                    item['name'],
                    item['content'],
                    item['business'],
                    item['company'],
                    item['position'],
                    item['education'],
                    item['major'],
                    item['gender'],
                    # 0,
                    item['avatar'],
                    item['agree'],
                    item['thanks']
                )
                print('创建user对象')
                print(user)
                self.session.add(user)
                self.session.commit()
            except Exception as e:
                print(e)

        return item


class AnswerPipeline(object):
    def __init__(self):
        engine = create_engine('sqlite:///test.db')
        Base.metadata.create_all(engine)
        SessionCls = sessionmaker(bind=engine)
        self.session = SessionCls()

    def process_item(self, item, spider):
        # temp = self.session.query(Answer).filter(User.url==item['url']).first()
        # if temp:
        #     pass
        # else:
        try:
            answer = Answer(
                item['url'],
                item['title'],
                item['detail'],
                item['content'],
                item['upvote_num'],
                item['timestamp'],
                item['user_name']
            )
            # answer.user_id = 1
            print('创建answer对象')
            print(answer)
            self.session.add(answer)
            self.session.commit()
        except Exception as e:
            print(e)

        return item
