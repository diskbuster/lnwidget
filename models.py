from sqlite3 import Row
from typing import NamedTuple


class lnwidget(NamedTuple):
    id: str
    wallet: str
    name: str
    currency: str

    @classmethod
    def from_row(cls, row: Row) -> "lnwidget":
        return cls(**dict(row))
