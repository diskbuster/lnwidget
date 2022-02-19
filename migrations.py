async def m001_initial(db):
    """
    Initial lnwidgets table.
    """
    await db.execute(
        """
        CREATE TABLE lnwidget.lnwidgets (
            id TEXT PRIMARY KEY,
            wallet TEXT NOT NULL,
            name TEXT NOT NULL,
            currency TEXT NOT NULL
        );
    """
    )
