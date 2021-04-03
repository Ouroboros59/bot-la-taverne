from sqlalchemy import Column, Integer, String, DATETIME, BOOLEAN, Table, ForeignKey
from sqlalchemy.orm import relationship

from Const import *

User_event = Table('User_event', Base.metadata,
                   Column('user_id', String(255), ForeignKey('user.id')),
                   Column('event_id', Integer, ForeignKey('event.id'))
                   )


class User(Base):
    __tablename__ = 'user'

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

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_message = Column(String(255), unique=True)
    max_user = Column(Integer)
    type = Column(String(255))
    date_closure = Column(DATETIME)
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

    id = Column(Integer, primary_key=True)
    name = Column(String(255))

    def __repr__(self):
        return "<AuthorizedRole(id='%s', name='%s')>" % (
            self.id, self.name)
