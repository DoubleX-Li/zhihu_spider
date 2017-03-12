from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    url = Column(String(255))
    name = Column(String(20))
    content = Column(String(255))
    business = Column(String(255))
    company = Column(String(255))
    position = Column(String(255))
    education = Column(String(255))
    major = Column(String(255))
    gender = Column(Integer)
    avatar = Column(String(255))
    agree = Column(Integer)
    thanks = Column(Integer)

    # answers = relationship('answers', backref='author')

    def __init__(self, url, name, content, business, company, position, education, major, gender, avatar, agree,
                 thanks):
        self.url = url
        self.name = name
        self.content = content
        self.business = business
        self.company = company
        self.position = position
        self.education = education
        self.major = major
        self.gender = gender
        self.avatar = avatar
        self.agree = agree
        self.thanks = thanks

    def __repr__(self):
        return 'User: %r' % self.name


class Answer(Base):
    __tablename__ = 'answers'

    id = Column(Integer, primary_key=True)
    url = Column(String(255))
    title = Column(String(255))
    detail = Column(Text)
    content = Column(Text)
    upvote_num = Column(Integer)
    timestamp = Column(String(255))
    # user_id = Column(Integer, ForeignKey('users.id'))

    def __init__(self, url, title, detail, content, upvote_num, timestamp):
        self.url = url
        self.title = title
        self.detail = detail
        self.content = content
        self.upvote_num = upvote_num
        self.timestamp = timestamp

    def __repr__(self):
        return 'Answer: %r' % self.url
