from sqlalchemy.orm import Mapped

from lib.orm import Base


UUID = "hmmm"


class Author(Base):
    name: Mapped[str]
