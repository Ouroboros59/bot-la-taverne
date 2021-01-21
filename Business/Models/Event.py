from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DATETIME

Base = declarative_base()


class Event(Base):
    __tablename__ = 'Event'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_message = Column(Integer, unique=True)
    date_closure = Column(DATETIME)

    def __repr__(self):
        return "<Event(id='%s', id_message='%s, date_closure='%s')>" % (
            self.id, self.id_message, self.date_closure)
