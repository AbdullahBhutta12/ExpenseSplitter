import requests
from fastapi import APIRouter, Request, Form, Depends, HTTPException, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from oauth2 import get_current_user_from_token
import schemas

import database
from repository import group, participant, expense, user

router = APIRouter(prefix="/frontend", tags=["Frontend Pages"])
templates = Jinja2Templates(directory="templates")



def get_current_user_from_cookie(request: Request, db: Session = Depends(database.get_db)):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not logged in")

    if token.startswith("Bearer "):
        token = token.split("Bearer ")[1]

    return get_current_user_from_token(token, db)



@router.get("/dashboard")
def dashboard(
    request: Request,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(get_current_user_from_cookie)
):
    # total groups
    groups = group.get_all(db, current_user.id)
    total_groups = len(groups)

    # total participants & expenses (all groups)
    total_participants = 0
    total_expenses = 0

    for g in groups:
        total_participants += len(participant.get_participants(db, g.id))
        total_expenses += len(expense.get_by_group(g.id, db))

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": current_user,
            "total_groups": total_groups,
            "total_participants": total_participants,
            "total_expenses": total_expenses
        }
    )


@router.get("/groups")
def groups_page(
    request: Request,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(get_current_user_from_cookie)
):
    groups = group.get_all(db, current_user.id)

    return templates.TemplateResponse(
        "groups.html",
        {"request": request, "groups": groups, "user": current_user}
    )


@router.get("/groups/{group_id}")
def group_detail(
    request: Request,
    group_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(get_current_user_from_cookie)
):
    g = group.get_by_id(db, group_id, current_user.id)

    if not g:
        return RedirectResponse("/frontend/groups", status_code=303)

    participants_list = participant.get_participants(db, group_id)
    expenses_list = expense.get_by_group(group_id, db)

    participant_map = {p.id: p.name for p in participants_list}

    expenses_view = []
    total_amount = 0

    for e in expenses_list:
        total_amount += float(e.amount or 0)

        expenses_view.append({
            "title": e.title,
            "amount": float(e.amount),
            "paid_by": participant_map.get(e.paid_by_id, f"ID {e.paid_by_id}"),
            "split_amount": 0
        })

    # Divide amount (TOTAL/participants)
    split_amount = 0
    if len(participants_list) > 0:
        split_amount = total_amount / len(participants_list)

    # split_amount for every expense
    for e in expenses_view:
        e["split_amount"] = float(split_amount)

    return templates.TemplateResponse(
        "group_detail.html",
        {
            "request": request,
            "group": g,
            "participants": participants_list,
            "expenses": expenses_view,
            "split_amount": split_amount,
            "total_amount": total_amount
        }
    )

@router.post("/groups")
def create_group(
    name: str = Form(...),
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(get_current_user_from_cookie)
):
    group.create(db, name, current_user.id)
    return RedirectResponse("/frontend/groups", status_code=303)




# EXPENSES

@router.get("/groups/{group_id}/add-expense")
def add_expense_page(
    request: Request,
    group_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(get_current_user_from_cookie)
):
    g = group.get_by_id(db, group_id, current_user.id)

    if not g:
        return RedirectResponse("/frontend/groups", status_code=303)

    participants = participant.get_participants(db, group_id)

    return templates.TemplateResponse(
        "add_expense.html",
        {
            "request": request,
            "group": g,
            "group_id": group_id,
            "participants": participants
        }
    )




@router.post("/groups/{group_id}/add-expense")
def add_expense_action(
    request: Request,
    group_id: int,
    title: str = Form(...),
    amount: float = Form(...),
    paid_by_id: int = Form(...),
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(get_current_user_from_cookie)
):
    g = group.get_by_id(db, group_id, current_user.id)
    if not g:
        return RedirectResponse("/frontend/groups", status_code=303)

    try:
        expense.create(db, group_id, title, amount, paid_by_id)
    except Exception:
        participants = participant.get_participants(db, group_id)
        return templates.TemplateResponse(
            "add_expense.html",
            {
                "request": request,
                "group": g,
                "participants": participants,
                "error": "Expense could not be added. Please try again."
            }
        )

    return RedirectResponse(f"/frontend/groups/{group_id}", status_code=303)



@router.get("/groups/{group_id}/add-participant")
def add_participant_page(
    request: Request,
    group_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(get_current_user_from_cookie)
):
    g = group.get_by_id(db, group_id, current_user.id)

    if not g:
        return RedirectResponse("/frontend/groups", status_code=303)

    return templates.TemplateResponse(
        "add_participant.html",
        {
            "request": request,
            "group": g,
            "group_id": group_id
        }
    )


@router.post("/groups/{group_id}/add-participant")
def add_participant_action(
    request: Request,
    group_id: int,
    name: str = Form(...),
    email: str = Form(""),
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(get_current_user_from_cookie)
):
    g = group.get_by_id(db, group_id, current_user.id)

    if not g:
        return RedirectResponse("/frontend/groups", status_code=303)

    try:
        participant.add_participant(db, group_id, name, email)
    except Exception:
        return templates.TemplateResponse(
            "add_participant.html",
            {
                "request": request,
                "group": g,
                "group_id": group_id,
                "error": "Participant could not be added. Try again."
            }
        )

    return RedirectResponse(f"/frontend/groups/{group_id}", status_code=303)



# Apis for sign-up and log-in

@router.get("/send-code")
def send_code_page(request: Request):
    return templates.TemplateResponse("send_code.html", {"request": request})


@router.post("/send-code-html")
async def send_code_html(
        request: Request,
        email: str = Form(...),
        db=Depends(database.get_db)
):
    data = schemas.Emails(email=email)

    try:
        user.send_code(data, db)
    except Exception as e:
        return templates.TemplateResponse(
            "send_code.html",
            {"request": request, "error": "OTP not sent. Try again."}
        )

    request.session["pending_email"] = email

    return RedirectResponse(url="/frontend/verify", status_code=303)



@router.get("/verify")
def verify_email_page(request: Request):
    email = request.session.get("pending_email")

    if not email:
        return RedirectResponse("/frontend/send-code", status_code=303)

    return templates.TemplateResponse(
        "verify_email.html",
        {"request": request, "email": email}
    )


@router.post("/verify")
def verify_email_html(
        request: Request,
        verification_code: str = Form(...),
        db=Depends(database.get_db)
):
    email = request.session.get("pending_email")
    if not email:
        return RedirectResponse("/frontend/send-code", status_code=303)

    data = schemas.VerifyEmail(email=email, verification_code=verification_code)

    try:
        user.verify_email(data, db)
        request.session.pop("pending_email", None)
        return RedirectResponse(url="/frontend/signup", status_code=303)

    except HTTPException as e:
        return templates.TemplateResponse(
            "verify_email.html",
            {
                "request": request,
                "email": email,
                "error": e.detail
            }
        )


@router.get("/signup")
def signup_page(request: Request):
    return templates.TemplateResponse(
        "signup.html",
        {"request": request, "error": None}
    )


@router.post("/signup")
def signup_action(
        request: Request,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        profile_image: UploadFile = File(...),
        db: Session = Depends(database.get_db)
):
    try:
        user.create(
            username=username,
            email=email,
            password=password,
            profile_image=profile_image,
            db=db
        )

        return RedirectResponse(url="/frontend/login", status_code=303)

    except HTTPException as e:
        # SAME signup page par error
        return templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "error": e.detail
            }
        )


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login_action(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
):
    payload = {
        "username": email,  # IMPORTANT
        "password": password
    }

    response = requests.post(
        "http://localhost:8000/login",
        data=payload
    )

    if response.status_code != 200:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid email or password"},
            status_code=400
        )

    token = response.json().get("access_token")

    redirect = RedirectResponse("/frontend/dashboard", status_code=303)
    redirect.set_cookie(key="access_token", value=token)

    return redirect


# Forgot password
@router.get("/forgot-password")
def forgot_password_page(request: Request):
    return templates.TemplateResponse(
        "forgot_password.html",
        {"request": request}
    )


@router.post("/forgot-password")
def forgot_password_action(
        request: Request,
        email: str = Form(...)
):
    try:
        r = requests.post(
            "http://localhost:8000/user/send-verification-code",
            json={"email": email},
            timeout=5
        )
    except Exception:
        return templates.TemplateResponse(
            "forgot_password.html",
            {
                "request": request,
                "error": "Server error. Please try again."
            }
        )

    if r.status_code != 200:
        return templates.TemplateResponse(
            "forgot_password.html",
            {
                "request": request,
                "error": r.json().get("detail", "OTP not sent")
            }
        )

    # save email in session
    request.session["reset_email"] = email
    return RedirectResponse("/frontend/verify-reset-otp", status_code=303)


# Verify OTP
@router.get("/verify-reset-otp")
def verify_reset_otp_page(request: Request):
    email = request.session.get("reset_email")

    if not email:
        return RedirectResponse("/frontend/forgot-password", status_code=303)

    return templates.TemplateResponse(
        "verify_reset_otp.html",
        {
            "request": request,
            "email": email
        }
    )


@router.post("/verify-reset-otp")
def verify_reset_otp_action(
        request: Request,
        otp: str = Form(...)
):
    email = request.session.get("reset_email")

    if not email:
        return RedirectResponse("/frontend/forgot-password", status_code=303)

    try:
        r = requests.post(
            "http://localhost:8000/user/verify-email",
            json={
                "email": email,
                "verification_code": otp
            },
            timeout=5
        )
    except Exception:
        return templates.TemplateResponse(
            "verify_reset_otp.html",
            {
                "request": request,
                "email": email,
                "error": "Server error. Try again."
            }
        )

    if r.status_code != 200:
        return templates.TemplateResponse(
            "verify_reset_otp.html",
            {
                "request": request,
                "email": email,
                "error": r.json().get("detail", "Invalid OTP")
            }
        )

    # OTP verified
    request.session["reset_verified"] = True
    return RedirectResponse("/frontend/reset-password", status_code=303)


# Reset password
@router.get("/reset-password")
def reset_password_page(request: Request):
    if not request.session.get("reset_verified"):
        return RedirectResponse("/frontend/forgot-password", status_code=303)

    return templates.TemplateResponse(
        "reset_password.html",
        {"request": request}
    )


@router.post("/reset-password")
def reset_password_action(
        request: Request,
        new_password: str = Form(...)
):
    email = request.session.get("reset_email")

    if not email:
        return RedirectResponse("/frontend/forgot-password", status_code=303)

    try:
        r = requests.post(
            "http://localhost:8000/user/reset-password",
            json={
                "email": email,
                "new_password": new_password
            },
            timeout=5
        )
    except Exception:
        return templates.TemplateResponse(
            "reset_password.html",
            {
                "request": request,
                "error": "Server error. Try again."
            }
        )

    if r.status_code != 200:
        return templates.TemplateResponse(
            "reset_password.html",
            {
                "request": request,
                "error": r.json().get("detail", "Password reset failed")
            }
        )

    # cleanup session
    request.session.pop("reset_email", None)
    request.session.pop("reset_verified", None)

    return RedirectResponse("/frontend/login", status_code=303)


@router.get('/profile')
def profile_page(request: Request):
    if "access_token" not in request.cookies:
        return RedirectResponse(url="/frontend/login")
    token = request.cookies.get("access_token")
    response = requests.get(
        "http://localhost:8000/user/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    profile = response.json()
    return templates.TemplateResponse("profile.html", {"request": request, "profile": profile})


@router.get("/logout")
def logout(request: Request):
    request.session.clear()

    response = RedirectResponse(url="/frontend/", status_code=303)
    response.delete_cookie("access_token")

    return response


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})
