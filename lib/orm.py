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


class Base(DeclarativeBase):
    """Base for all SQLAlchemy declarative models."""

    registry = registry(
        metadata=MetaData(),
        type_annotation_map={UUID: pg.UUID, dict: pg.JSONB},
    )

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)

    # noinspection PyMethodParameters
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
