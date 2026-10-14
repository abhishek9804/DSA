import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.tenancy import (
    get_current_membership,
    require_admin,
)
from app.db.session import get_db
from app.models.membership import TenantMembership, TenantRole
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.tenant import (
    MembershipCreate,
    MembershipResponse,
    TenantCreate,
    TenantResponse,
)


router = APIRouter(
    prefix="/tenants",
    tags=["Tenants"],
)


@router.post(
    "",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_tenant(
    payload: TenantCreate,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> Tenant:
    existing_tenant = db.scalar(
        select(Tenant).where(Tenant.slug == payload.slug)
    )

    if existing_tenant:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tenant slug already exists",
        )

    tenant = Tenant(
        name=payload.name.strip(),
        slug=payload.slug,
    )

    db.add(tenant)
    db.flush()

    membership = TenantMembership(
        user_id=current_user.id,
        tenant_id=tenant.id,
        role=TenantRole.ADMIN,
    )

    db.add(membership)
    db.commit()
    db.refresh(tenant)

    return tenant


@router.get(
    "",
    response_model=list[TenantResponse],
)
def list_my_tenants(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> list[Tenant]:
    statement = (
        select(Tenant)
        .join(TenantMembership)
        .where(TenantMembership.user_id == current_user.id)
        .order_by(Tenant.name)
    )

    return list(db.scalars(statement).all())


@router.get(
    "/{tenant_id}",
    response_model=TenantResponse,
)
def get_tenant(
    membership: Annotated[
        TenantMembership,
        Depends(get_current_membership),
    ],
) -> Tenant:
    return membership.tenant


@router.get(
    "/{tenant_id}/members",
    response_model=list[MembershipResponse],
)
def list_members(
    tenant_id: uuid.UUID,
    _: Annotated[
        TenantMembership,
        Depends(get_current_membership),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> list[TenantMembership]:
    statement = (
        select(TenantMembership)
        .where(TenantMembership.tenant_id == tenant_id)
        .order_by(TenantMembership.created_at)
    )

    return list(db.scalars(statement).all())


@router.post(
    "/{tenant_id}/members",
    response_model=MembershipResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_member(
    tenant_id: uuid.UUID,
    payload: MembershipCreate,
    _: Annotated[
        TenantMembership,
        Depends(require_admin),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> TenantMembership:
    user = db.scalar(
        select(User).where(
            User.email == payload.email.lower()
        )
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    existing_membership = db.scalar(
        select(TenantMembership).where(
            TenantMembership.user_id == user.id,
            TenantMembership.tenant_id == tenant_id,
        )
    )

    if existing_membership:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this tenant",
        )

    membership = TenantMembership(
        user_id=user.id,
        tenant_id=tenant_id,
        role=payload.role,
    )

    db.add(membership)
    db.commit()
    db.refresh(membership)

    return membership