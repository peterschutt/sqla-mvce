"""Application ORM configuration."""
from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import MetaData
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    registry,
)

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
"""
Templates for automated constraint name generation.
"""


class Base(DeclarativeBase):
    """Base for all SQLAlchemy declarative models."""

    registry = registry(
        metadata=MetaData(naming_convention=convention),
        type_annotation_map={UUID: pg.UUID, dict: pg.JSONB},
    )

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)

    # noinspection PyMethodParameters
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
