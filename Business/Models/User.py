from sqlalchemy import Column, String, Table, Integer, ForeignKey, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

eventUserRegister = Table('Event_user_register',
                          Base.metadata,
                          Column('event_id', Integer, ForeignKey('Event.id'), primary_key=True),
                          Column('user_id', Integer, ForeignKey('User.id'), primary_key=True))


class User(Base):
    __tablename__ = 'user'

    id = Column(String, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return "<User(id='%s', name='%s')>" % (
            self.id, self.name)
