from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    uid = Column(String(255))
    name = Column(String(20))
    motto = Column(String(255))
    location = Column(String(255))
    business = Column(String(255))
    company = Column(String(255))
    education = Column(String(255))
    content = Column(String(255))
    avatar = Column(String(255))
    agree = Column(Integer)

    def __init__(self, uid, name, content, location, business, company, education, motto, avatar, agree):
        self.uid = uid
        self.name = name
        self.content = content
        self.location = location
        self.business = business
        self.company = company
        self.education = education
        self.motto = motto
        self.avatar = avatar
        self.agree = agree

    def __repr__(self):
        return 'User: %r' % self.uid


class Following(Base):
    __tablename__ = 'following'

    id = Column(Integer, primary_key=True)
    uid = Column(String(255))
    followed_by = Column(String(255))

    def __init__(self, uid, followed_by):
        self.uid = uid
        self.followed_by = followed_by

    def __repr__(self):
        return '{0} --> {1}'.format(self.followed_by, self.uid)


class Answer(Base):
    __tablename__ = 'answers'

    id = Column(Integer, primary_key=True)
    url = Column(String(255))
    title = Column(String(255))
    detail = Column(Text)
    content = Column(Text)
    upvote_num = Column(Integer)
    timestamp = Column(String(255))
    user_name = Column(String(255))

    def __init__(self, url, title, detail, content, upvote_num, timestamp, user_name):
        self.url = url
        self.title = title
        self.detail = detail
        self.content = content
        self.upvote_num = upvote_num
        self.timestamp = timestamp
        self.user_name = user_name

    def __repr__(self):
        return 'Answer: %r' % self.url
