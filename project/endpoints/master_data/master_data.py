from datetime import datetime, timezone
from sqlalchemy import and_
from datetime import datetime
from ...models.admin_user import AdminUser
from ...models.master_data_models import MdUserRole,MdUserStatus

from . import APIRouter, Utility, SUCCESS, FAIL, EXCEPTION, Depends, Session, get_database_session, AuthHandler
from ...schemas.register import AdminRegister
import re
from ...schemas.master_data import getMasterData
import os
import json
from pathlib import Path
from ...models.master_data_models import MdCountries,MdLocations,MdReminderStatus,MdStates,MdTaskStatus,MdTenantStatus,MdTimeZone,MdUserRole,MdUserStatus
# APIRouter creates path operations for product module
from ...constant.messages import MASTER_DATA_LIST

router = APIRouter(
    prefix="/masterdata",
    tags=["Master Data"],
    responses={404: {"description": "Not found"}},
)
file_to_model = {
            "md_countries.json": MdCountries,
            "md_states.json": MdStates,
            "md_locations.json": MdLocations,
            "md_reminder_status.json": MdReminderStatus,
            "md_task_status.json": MdTaskStatus,
            "md_tenant_status.json": MdTenantStatus,
            "md_timezone.json": MdTimeZone,
            "md_user_roles.json": MdUserRole,
            "md_user_status.json": MdUserStatus 
        }



@router.get("/migrate", response_description="Migrate Master Data")
def get_users(db: Session = Depends(get_database_session)):
       
    try:
        #return {"status": "FAIL", "message": "Data migrated successfully"}
        
        json_directory = Path(__file__).resolve().parent.parent.parent / "migrate_data"
        

        batch_size = 500

        for filename in os.listdir(json_directory):
            if filename in file_to_model:
                model = file_to_model[filename]
                file_path = json_directory / filename
                
                with open(file_path, 'r') as file:
                    data = json.load(file)

                batch = []
                for entry in data:
                    # Filter out any keys not matching the model's attributes
                    filtered_entry = {key: value for key, value in entry.items() if hasattr(model, key)}
                    
                    record = model(**filtered_entry)
                    batch.append(record)

                    if len(batch) >= batch_size:
                        db.bulk_save_objects(batch)
                        batch.clear()

                if batch:
                    db.bulk_save_objects(batch)

                db.commit()

        return {"status": "SUCCESS", "message": "Data migrated successfully"}

    except Exception as e:
        db.rollback()
        print(e)
        return {"status": "FAIL", "message": "Something went wrong"}

@router.post("/get-master-data", response_description="Migrate Master Data")
def get_users(request: getMasterData ,db: Session = Depends(get_database_session)):
       
    try:
        categories = request.categories
        country_id = None
        state_id = None
        if request.country_id:
            country_id = request.country_id
        if request.state_id :
            state_id = request.state_id    

        
        output ={}
        
        for category in categories:
            if category+".json" in file_to_model:
                model = file_to_model[category+".json"]
                if category=="md_states" and country_id:
                    records = db.query(model).filter(model.countryId==int(country_id)).all()
                    output[category] =  [Utility.model_to_dict(record) for record in records]
                elif category=="md_locations" and state_id:
                    records = db.query(model).filter(model.stateId==int(state_id)).all()
                    output[category] =  [Utility.model_to_dict(record) for record in records]
                else:    
                    records = db.query(model).all()
                    output[category] =  [Utility.model_to_dict(record) for record in records]

        return Utility.json_response(status=FAIL, message=MASTER_DATA_LIST, error=[], data=output)
    except Exception as e:        
        db.rollback()
        return {"status": "FAIL", "message": "Something went wrong"}
