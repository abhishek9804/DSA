import enum
import uuid
from datetime import datetime
from sqlalchemy import DateTime, Enum, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped,mapped_column, relationship
from app.db.base import Base

class TenantRole(str, enum.Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIWER = "viewer"

class TenantMembership(Base):
    __tablename__ = "tenant_memberships"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "tenant_id",
            name="uq_user_tenant_membership",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role: Mapped[TenantRole] = mapped_column(
        Enum(
            TenantRole,
            name="tenant_role",
            values_callable=lambda enum_class:[
                item.value for item in enum_class
            ],
        ),
        default=TenantRole.VIWER,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="memberships",
    )

    tenant = relationship(
        "Tenant",
        back_populates="memberships",
    )