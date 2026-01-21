from sqlalchemy.orm import Session
import models

def add_participant(db: Session, group_id: int, name: str, email=None):
    participant = models.Participant(
        name=name,
        email=email,
        group_id=group_id
    )
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant


def get_participants(db: Session, group_id: int):
    return db.query(models.Participant).filter(models.Participant.group_id == group_id).all()

