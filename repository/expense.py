from sqlalchemy.orm import Session
import models

def create(db: Session, group_id: int, title: str, amount: float, paid_by_id: int):
    expense = models.Expense(
        title=title,
        amount=amount,
        group_id=group_id,
        paid_by_id=paid_by_id
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense

def calculate_equal_split(db: Session, group_id: int):
    participants = db.query(models.Participant).filter(models.Participant.group_id == group_id).all()
    expenses = db.query(models.Expense).filter(models.Expense.group_id == group_id).all()

    count_participants = len(participants)

    result = []

    for e in expenses:
        paid_by_name = "Unknown"
        if e.paid_by:
            paid_by_name = e.paid_by.name

        split_amount = (e.amount / count_participants) if count_participants > 0 else 0

        result.append({
            "title": e.title,
            "amount": float(e.amount),
            "paid_by": paid_by_name,
            "split_amount": float(split_amount)
        })

    return result

def get_by_group(group_id: int, db: Session):
    return db.query(models.Expense).filter(models.Expense.group_id == group_id).all()
