from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import database, schemas, oauth2
from repository import group

router = APIRouter(prefix="/groups", tags=["Groups"])

@router.post("/")
def create_group(request: schemas.GroupCreate, db: Session = Depends(database.get_db), current_user = Depends(oauth2.get_current_user)):
    return group.create(db, request.name, current_user.id)


@router.get("/")
def get_groups(db: Session = Depends(database.get_db), current_user = Depends(oauth2.get_current_user)):
    return group.get_all(db, current_user.id)
