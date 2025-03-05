from sqlalchemy import Column,Integer,String,Boolean
from sqlalchemy.sql.expression import null
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Person(Base) :
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False,autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)

    