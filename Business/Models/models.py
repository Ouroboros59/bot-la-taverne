from sqlalchemy import Column, Integer, String, BOOLEAN, Table, ForeignKey, create_engine, TIMESTAMP, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from Const import *

engine = create_engine(
    f'{DB_DIALECT}://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT.__str__()}/{DB_DB}',
    echo=True)

Base = declarative_base()
User_event = Table('User_event', Base.metadata,
                   Column('user_id', String(255), ForeignKey('test.user.id')),
                   Column('event_id', Integer, ForeignKey('test.event.id')),
                   schema=DB_SCHEMA
                   )


class User(Base):
    __tablename__ = 'user'
    __table_args__ = {'schema': DB_SCHEMA}
    id = Column(String(255), primary_key=True)
    name = Column(String(255))
    events = relationship(
        'Event',
        secondary=User_event,
        back_populates="users"
    )

    def __repr__(self):
        return "<User(id='%s', name='%s')>" % (
            self.id, self.name)


class Event(Base):
    __tablename__ = 'event'
    __table_args__ = {'schema': DB_SCHEMA}
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_message = Column(String(255), unique=True)
    max_user = Column(Integer)
    type = Column(String(255))
    date_closure = Column(TIMESTAMP)
    open = Column(BOOLEAN, default=True)
    users = relationship(
        "User",
        secondary=User_event,
        back_populates="events")

    def __repr__(self):
        return "<Event(id='%s', id_message='%s, date_closure='%s')>" % (
            self.id, self.id_message, self.date_closure.strftime("%m/%d/%Y, %H:%M:%S"))


class AuthorizedRole(Base):
    __tablename__ = 'authorized_role'
    __table_args__ = {'schema': DB_SCHEMA}
    id = Column(String(255), primary_key=True)
    name = Column(String(255))

    def __repr__(self):
        return "<AuthorizedRole(id='%s', name='%s')>" % (
            self.id, self.name)


Session = sessionmaker(engine)
session = Session()
Base.metadata.create_all(engine)
