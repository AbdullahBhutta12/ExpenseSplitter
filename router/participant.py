from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import database, schemas
from repository import participant

router = APIRouter(prefix="/participants", tags=["Participants"])

@router.post("/{group_id}")
def add_participant(
    group_id: int,
    request: schemas.ParticipantCreate,
    db: Session = Depends(database.get_db)
):
    return participant.add_participant(db, group_id, request.name, request.email)

@router.get("/{group_id}")
def get_participant(
    group_id: int,
    db: Session = Depends(database.get_db)
):
    return participant.get_participants(db, group_id)