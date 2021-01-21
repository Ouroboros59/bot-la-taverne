from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class AuthorizedRole(Base):
    __tablename__ = 'Authorized_role'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return "<AuthorizedRole(id='%s', name='%s')>" % (
            self.id, self.name)
