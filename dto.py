from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Location(Base):
    __tablename__ = 'location'
    
    id = Column(Integer, primary_key=True)
    x = Column(Float)
    y = Column(Float)
    country_name = Column(String)

class Profile(Base):
    __tablename__ = 'profile'
    
    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey('location.id'))
    profile_layer_id = Column(Integer)
    upper_depth = Column(Integer)
    lower_depth = Column(Integer)
    layer_name = Column(String)
    location = relationship('Location', back_populates='profiles')


class Orgc(Base):
    __tablename__ = 'orgc'
    
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profile.id'))
    orgcmethod_id = Column(Integer, ForeignKey('orgcmethod.id'))
    orgc_value_avg = Column(Float)
    orgc_dataset_id = Column(String)
    orgc_profile_code = Column(String)
    profile = relationship('Profile', back_populates='orgc')
    orgcmethod = relationship('Orgcmethod', back_populates='orgc')
    


class Orgcmethod(Base):
    __tablename__ = 'orgcmethod'
    id = Column(Integer, primary_key=True)
    calculation = Column(String)
    detection = Column(String)
    reaction = Column(String)
    sample_pretreatment = Column(String)
    temperature = Column(String)
    treatment = Column(String)
    #orgc = relationship('Orgc', back_populates='orgcmethod')