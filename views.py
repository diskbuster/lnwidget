from quart import g, abort, render_template
from http import HTTPStatus

from lnbits.decorators import check_user_exists, validate_uuids

from . import lnwidget_ext
from .crud import get_lnwidget


@lnwidget_ext.route("/")
@validate_uuids(["usr"], required=True)
@check_user_exists()
async def index():
    return await render_template("lnwidget/index.html", user=g.user)


@lnwidget_ext.route("/<lnwidget_id>")
async def lnwidget(lnwidget_id):
    lnwidget = await get_lnwidget(lnwidget_id)
    if not lnwidget:
        abort(HTTPStatus.NOT_FOUND, "lnwidget does not exist.")

    return await render_template("lnwidget/lnwidget.html", lnwidget=lnwidget)
