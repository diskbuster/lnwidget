from typing import List, Optional, Union

from lnbits.helpers import urlsafe_short_hash

from . import db
from .models import lnwidget


async def create_lnwidget(*, wallet_id: str, name: str, currency: str) -> lnwidget:
    lnwidget_id = urlsafe_short_hash()
    await db.execute(
        """
        INSERT INTO lnwidget.lnwidgets (id, wallet, name, currency)
        VALUES (?, ?, ?, ?)
        """,
        (lnwidget_id, wallet_id, name, currency),
    )

    lnwidget = await get_lnwidget(lnwidget_id)
    assert lnwidget, "Newly created lnwidget couldn't be retrieved"
    return lnwidget


async def get_lnwidget(lnwidget_id: str) -> Optional[lnwidget]:
    row = await db.fetchone("SELECT * FROM lnwidget.lnwidgets WHERE id = ?", (lnwidget_id,))
    return lnwidget.from_row(row) if row else None


async def get_lnwidgets(wallet_ids: Union[str, List[str]]) -> List[lnwidget]:
    if isinstance(wallet_ids, str):
        wallet_ids = [wallet_ids]

    q = ",".join(["?"] * len(wallet_ids))
    rows = await db.fetchall(
        f"SELECT * FROM lnwidget.lnwidgets WHERE wallet IN ({q})", (*wallet_ids,)
    )

    return [lnwidget.from_row(row) for row in rows]


async def delete_lnwidget(lnwidget_id: str) -> None:
    await db.execute("DELETE FROM lnwidget.lnwidgets WHERE id = ?", (lnwidget_id,))
