from datetime import datetime, timezone,timedelta
from sqlalchemy import and_
from datetime import datetime
from ...models.user_model import UserModel
from ...models.master_data_models import MdUserRole,MdUserStatus

from . import APIRouter, Utility, SUCCESS, FAIL, EXCEPTION, Depends, Session, get_database_session, AuthHandler
from ...schemas.register import Register
import re
from ...schemas.login import Login
from ...constant import messages as all_messages
from ...common.mail import Email

# APIRouter creates path operations for product module
router = APIRouter(
    prefix="/User",
    tags=["User Authentication"],
    responses={404: {"description": "Not found"}},
)

@router.post("/user-register", response_description="User User Registration")
async def register(request: Register, db: Session = Depends(get_database_session)):
    try:
        
        mobile_no = request.mobile_no
        email = request.email
        country_id = request.country_id
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        if not re.fullmatch(email_regex, email):
            return Utility.json_response(status=FAIL, message=all_messages.INVALIED_EMAIL, error=[], data={})
        
        
        if len(str(mobile_no)) < 7 or len(str(mobile_no)) > 15:
            return Utility.json_response(status=FAIL, message=all_messages.INVALIED_MOBILE,error=[], data={})
        user_obj = db.query(UserModel).filter(UserModel.email == email)
        if user_obj.count() <=0:
            user_data = UserModel(role_id =2,status_id=1, email=email,country_id=country_id, mobile_no=mobile_no,password=str(Utility.uuid()))
            #Send Mail to user with active link
            Email.send_mail(recipient_email=[email], subject=all_messages.SIGNUP_MAIL_SUBJECT, template='',data={} )
            db.add(user_data)
            db.flush()
            db.commit()
            if user_data.id:
                return Utility.json_response(status=SUCCESS, message=all_messages.REGISTER_SUCCESS, error=[],data={"user_id": user_data.id})
            else:
                db.rollback()
                return Utility.json_response(status=FAIL, message=all_messages.SOMTHING_WRONG, error=[], data={})
        else:
            new_user = user_obj.one()
            if new_user.status_id == 1:
                otp =Utility.generate_otp()
                mail_data = {"body":str(otp)}
                user_obj.update({ UserModel.otp:otp}, synchronize_session=False)
                db.flush()
                db.commit()
                Email.send_mail(recipient_email=[email], subject=all_messages.PENDING_EMAIL_VERIFICATION_OTP_SUBJ, template='',data=mail_data )               
                return Utility.json_response(status=SUCCESS, message=all_messages.ACCOUNT_EXISTS_PENDING_EMAIL_VERIFICATION, error=[], data={},code="EMAIL_VERIFICATION_PENDING")
            elif  new_user.status_id == 2:
                return Utility.json_response(status=FAIL, message=all_messages.PROFILE_IS_ACTIVE, error=[], data={},code="PROFILE_IS_ACTIVE")
            elif new_user.status_id == 3:
                return Utility.json_response(status=SUCCESS, message=all_messages.PROFILE_ACTIVE, error=[], data={})
            elif new_user.status_id == 4:
                return Utility.json_response(status=SUCCESS, message=all_messages.PROFILE_DELETED, error=[], data={})
            else:
                db.rollback()
                return Utility.json_response(status=FAIL, message=all_messages.SOMTHING_WRONG, error=[], data={})

    except Exception as E:
        
        db.rollback()
        return Utility.json_response(status=FAIL, message=all_messages.SOMTHING_WRONG, error=[], data={})


@router.post("/login", response_description="Admin authenticated")
def admin_login(request: Login, db: Session = Depends(get_database_session)):
    try:
        
        email = request.email
        password = request.password
        user_obj = db.query(UserModel,
                        #UserModel.email,
                        #UserModel.status_id,
                        #UserModel.user_name,
                        #UserModel.login_token,
                        #UserModel.password,
                        #UserModel.id
                        ).filter(UserModel.email == email)
       
        if user_obj.count() != 1:
            return Utility.json_response(status=FAIL, message=all_messages.INVALIED_CREDENTIALS, error=[], data={})
        user_data = user_obj.one()
        
        if user_data.status_id !=2:
            
            msg = all_messages.PROFILE_INACTIVE
            if user_data.status_id == 1:
                msg = all_messages.PENDING_EMAIL_VERIFICATION
                
            elif user_data.status_id == 3:
                msg = all_messages.PROFILE_INACTIVE
            elif user_data.status_id == 4:
                msg = all_messages.PROFILE_DELETED
            return Utility.json_response(status=FAIL, message=msg, error=[], data={})
        else:
            
            verify_password = AuthHandler().verify_password(str(password), user_data.password)
            if not verify_password:
                login_fail_count = user_data.login_fail_count
                if login_fail_count >=3:
                    current_time = datetime.utcnow()
                    time_difference = current_time - user_data.login_attempt_date
                    if time_difference >= timedelta(hours=24):
                        print("24 Completed")
                        user_obj.update({ UserModel.login_attempt_date:datetime.utcnow(),UserModel.login_fail_count:0}, synchronize_session=False)
                        db.flush()
                        db.commit()
                    else:
                        print("24 Not Completed")
                        # Access denied (less than 24 hours since last login)
                        user_obj.update({UserModel.login_fail_count:UserModel.login_fail_count+1}, synchronize_session=False)
                        db.flush()
                        db.commit()
                        #ACCOUNT_LOCKED
                        return Utility.json_response(status=FAIL, message=all_messages.ACCOUNT_LOCKED, error=[], data={})
                    #Wit for 24 Hourse
                else:
                    user_obj.update({ UserModel.login_attempt_date:datetime.utcnow(),UserModel.login_fail_count:UserModel.login_fail_count+1}, synchronize_session=False)
                    db.flush()
                    db.commit()
                return Utility.json_response(status=FAIL, message=all_messages.INVALIED_CREDENTIALS, error=[], data={})
            else:
                login_token = AuthHandler().encode_token(user_dict)
                if not login_token:
                    return Utility.json_response(status=FAIL, message=all_messages.SOMTHING_WRONG, error=[], data={})
                else:
                    user_dict = Utility.model_to_dict(user_data)
                    #user_dict = {c.name: getattr(user_data, c.name) for c in user_data.__table__.columns}
                    #print(user_dict)
                    if "password" in user_dict:
                        del user_dict["password"]
                    if "token" in user_dict:
                        del user_dict["token"]
                    user_data.login_token = login_token
                    del user_data.password
                    del user_data.login_token
                    return Utility.dict_response(status=SUCCESS, message=all_messages.SUCCESS_LOGIN, error=[], data=user_data)

    except Exception as E:
        
        print(E)
        db.rollback()
        return Utility.json_response(status=EXCEPTION, message="Something went wrong", error=[], data={})
