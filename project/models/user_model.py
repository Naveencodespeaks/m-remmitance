from sqlalchemy import Column, Integer,INT, String, Text, DateTime, ForeignKey,Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
#from project.database.database import Base
#Base = declarative_base()
from  .base_model import BaseModel
from datetime import datetime
from enum import Enum as PyEnum
class kycStatus(PyEnum):
    PENDING = 0
    COMPLETED = 1
    

class UserModel(BaseModel):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(61))
    password = Column(Text)
    login_token = Column(Text)
    email = Column(String(161), nullable=False )
    mobile_no = Column(String(13), default="")
    last_login = Column(DateTime, default= datetime.utcnow() )
    kyc_status = Column(Enum(kycStatus), nullable=False, default=kycStatus.PENDING,comment='The status of the user (e.g., pending==0, completed==1)')
    login_fail_count =  Column(Integer, default=0,comment='User Login Fail count')
    login_attempt_date = Column(DateTime, default= None,comment='Last Login Attempt date' )
    otp=Column(String(61))
    tenant_id = Column(Integer, nullable=True)
    role_id = Column(Integer, ForeignKey('md_user_roles.id'), nullable=False,default=1)  # Ensure this matches UserRole.id
    role_details = relationship('MdUserRole', back_populates='user')

    status_id = Column(Integer, ForeignKey('md_user_status.id'),  nullable=False,default=1)
    status_details = relationship('MdUserStatus', back_populates='user_status')

    user_details = relationship("UserDetails", back_populates="user")

    country_id = Column(Integer, ForeignKey("md_countries.id"), nullable=False, default=None )
    country_details = relationship("MdCountries", back_populates="user_country")
    

    state_id = Column(Integer, ForeignKey("md_states.id"), nullable=True, default=None )
    location_id = Column(Integer, ForeignKey("md_locations.id"), nullable=True, index=True )

    class Config:
        orm_mode = True

class UserDetails(BaseModel):
    __tablename__ = "user_detais"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id =  Column(Integer, ForeignKey("users.id"), nullable=False, index=True,unique=True )
    user = relationship("UserModel", back_populates="user_details")

    
