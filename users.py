from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from dependencies import get_current_user, get_current_admin
from limiter import limiter
from model import User
from schemas import UserCreate, UserResponse, Token
from security import hash_password, verify_password, create_access_token

router = APIRouter(
    prefix="/users",
    tags=["User"]
)


def check_self_or_admin(user_id: int, current_user: User):
    # Sirf apna account ya admin
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not allowed")


#--- REGISTER (public) ---
@router.post("/", response_model=UserResponse, status_code=201)
@limiter.limit("10/minute")
def user_create(
    request: Request,
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        phone=user.phone
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Could not create user; email may already exist"
        )

    return new_user


#--- LOGIN (public) ---
@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def user_login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}


#--- MY PROFILE ---
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


#--- GET ALL USERS (admin only) ---
@router.get("/", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    return db.query(User).all()


#--- GET USER BY ID (self or admin) ---
@router.get("/{user_id}", response_model=UserResponse)
def user_get_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_self_or_admin(user_id, current_user)

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


#--- UPDATE USER (self or admin) ---
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    updated_user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_self_or_admin(user_id, current_user)

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if updated_user.email != user.email:
        email_taken = db.query(User).filter(
            User.email == updated_user.email
        ).first()

        if email_taken:
            raise HTTPException(status_code=409, detail="Email already registered")

    user.name = updated_user.name
    user.email = updated_user.email
    user.password = hash_password(updated_user.password)
    user.phone = updated_user.phone

    db.commit()
    db.refresh(user)

    return user


#--- DELETE USER (admin only) ---
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        db.delete(user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="User has orders and cannot be deleted"
        )

    return {"message": "User deleted successfully"}