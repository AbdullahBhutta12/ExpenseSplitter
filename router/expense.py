from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import database, schemas
from repository import expense

router = APIRouter(prefix="/expenses", tags=["Expenses"])

@router.post("/{group_id}")
def add_expense(
    group_id: int,
    request: schemas.ExpenseCreate,
    db: Session = Depends(database.get_db)
):
    return expense.create(
        db,
        group_id,
        request.title,
        request.amount,
        request.paid_by_id
    )


@router.get("/split/{group_id}")
def get_split(
    group_id: int,
    db: Session = Depends(database.get_db)
):
    return expense.calculate_equal_split(db, group_id)



