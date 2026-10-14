from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.core.security import(
    create_access_token,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(payload: UserCreate, db: Annotated[Session, Depends(get_db)]) -> User:
    normalized_email = payload.email.lower()

    existing_user = db.scalar(
        select(User).where(User.email == normalized_email)
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )
    
    user = User(
        email = normalized_email,
        full_name = payload.full_name.strip(),
        password_hash = hash_password(payload.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[Session, Depends(get_db)],) -> TokenResponse:
    email = form_data.username.lower()

    user = db.scalar(
        select(User).where(User.email == email)
    )

    if user is None or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail= "Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    return TokenResponse(
        access_token = create_access_token(user.id),
    )

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_my_profile(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user

