from sqlalchemy.orm import Mapped

from lib.orm import Base


class Author(Base):
    name: Mapped[str]
