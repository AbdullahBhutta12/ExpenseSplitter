from sqlalchemy.orm import Session
import models


def create(db: Session, name: str, owner_id: int):
    group = models.Group(
        name=name,
        owner_id=owner_id
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def get_all(db: Session, user_id: int):
    return db.query(models.Group).filter(
        models.Group.owner_id == user_id
    ).all()


def get_by_id(db: Session, group_id: int, user_id: int):
    return db.query(models.Group).filter(
        models.Group.id == group_id,
        models.Group.owner_id == user_id
    ).first()