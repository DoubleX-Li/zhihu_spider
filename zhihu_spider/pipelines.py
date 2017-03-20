# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from zhihu_spider.models import Base, User, Answer, Following


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
        if item['type'] == 'user':
            temp = self.session.query(User).filter(User.uid == item['uid']).first()
            if temp:
                pass
            else:
                try:
                    user = User(
                        item['uid'],
                        item['name'],
                        item['content'],
                        item['location'],
                        item['business'],
                        item['company'],
                        item['education'],
                        item['motto'],
                        item['avatar'],
                        item['agree']
                    )
                    print('创建user对象')
                    print(user)
                    self.session.add(user)
                    self.session.commit()
                except Exception as e:
                    print(e)
        elif item['type'] == 'following':
            try:
                following = Following(
                    item['uid'],
                    item['followed_by']
                )
                print('创建following对象')
                print(following)
                self.session.add(following)
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
