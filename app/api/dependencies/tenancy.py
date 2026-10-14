import uuid
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.models.membership import TenantMembership, TenantRole
from app.models.user import User

def get_current_membership(tenant_id: Annotated[uuid.UUID, Path()], current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> TenantMembership:
    membership = db.scalar(
        select(TenantMembership).where(
            TenantMembership.tenant_id == tenant_id,
            TenantMembership.user_id == current_user.id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    return membership

def require_roles(*allowed_roles: TenantRole) -> Callable:
    def role_dependency(membership: Annotated[TenantMembership,Depends(get_current_membership) ]) -> TenantMembership:
        if membership.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient tenant permissions",
            )
        return membership
    
    return role_dependency

require_admin = require_roles(TenantRole.ADMIN)

require_editor_or_admin = require_roles(
    TenantRole.ADMIN,
    TenantRole.EDITOR,
)

