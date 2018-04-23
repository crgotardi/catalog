import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()


# user table
class User(Base):
    __tablename__ = 'user'

    name = Column(String(80), nullable=False)
    email = Column(String(80))
    picture = Column(String(80))
    id = Column(Integer, primary_key=True)


# catalog table
class Catalog(Base):
    __tablename__ = 'catalog'

    category = Column(String(80), nullable=False)
    description = Column(String(80))
    img_url = Column(String(150))
    id = Column(Integer, primary_key=True)

    @property
    def serialize(self):
        return {
            'name': self.category,
            'id': self.id,
        }


# item table
class Item(Base):
    __tablename__ = 'item'

    name = Column(String(80), nullable=False)
    description = Column(String(80))
    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    img_url = Column(String(150))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    catalog_id = Column(Integer, ForeignKey('catalog.id'))
    catalog = relationship(Catalog)

    # JSON endpoint
    @property
    def serialize(self):
        return {
            'cat_id': self.catalog_id,
            'description': self.description,
            'id': self.id,
            'name': self.name,
        }


engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)
