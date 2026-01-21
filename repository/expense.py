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

    if not participants:
        return []

    total_expense = sum(exp.amount for exp in expenses)
    share = total_expense / len(participants)

    balances = {p.id: 0 for p in participants}

    for exp in expenses:
        balances[exp.paid_by_id] += exp.amount

    for p in participants:
        balances[p.id] -= share

    result = []
    for p in participants:
        result.append({
            "participant_name": p.name,
            "balance": round(balances[p.id], 2)
        })

    return result


def get_by_group(group_id: int, db: Session):
    return db.query(models.Expense).filter(models.Expense.group_id == group_id).all()
