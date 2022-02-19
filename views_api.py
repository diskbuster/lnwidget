from quart import g, jsonify, request
from http import HTTPStatus

from lnbits.core.crud import get_user, get_wallet
from lnbits.core.services import create_invoice, check_invoice_status
from lnbits.decorators import api_check_wallet_key, api_validate_post_request

from . import lnwidget_ext
from .crud import create_lnwidget, get_lnwidget, get_lnwidgets, delete_lnwidget


@lnwidget_ext.route("/api/v1/lnwidgets", methods=["GET"])
@api_check_wallet_key("invoice")
async def api_lnwidgets():
    wallet_ids = [g.wallet.id]
    if "all_wallets" in request.args:
        wallet_ids = (await get_user(g.wallet.user)).wallet_ids

    return (
        jsonify([lnwidget._asdict() for lnwidget in await get_lnwidgets(wallet_ids)]),
        HTTPStatus.OK,
    )


@lnwidget_ext.route("/api/v1/lnwidgets", methods=["POST"])
@api_check_wallet_key("invoice")
@api_validate_post_request(
    schema={
        "name": {"type": "string", "empty": False, "required": True},
        "currency": {"type": "string", "empty": False, "required": True},
    }
)
async def api_lnwidget_create():
    lnwidget = await create_lnwidget(wallet_id=g.wallet.id, **g.data)
    return jsonify(lnwidget._asdict()), HTTPStatus.CREATED


@lnwidget_ext.route("/api/v1/lnwidgets/<lnwidget_id>", methods=["DELETE"])
@api_check_wallet_key("admin")
async def api_lnwidget_delete(lnwidget_id):
    lnwidget = await get_lnwidget(lnwidget_id)

    if not lnwidget:
        return jsonify({"message": "lnwidget does not exist."}), HTTPStatus.NOT_FOUND

    if lnwidget.wallet != g.wallet.id:
        return jsonify({"message": "Not your lnwidget."}), HTTPStatus.FORBIDDEN

    await delete_lnwidget(lnwidget_id)

    return "", HTTPStatus.NO_CONTENT


@lnwidget_ext.route("/api/v1/lnwidgets/<lnwidget_id>/invoices/", methods=["POST"])
@api_validate_post_request(
    schema={"amount": {"type": "integer", "min": 1, "required": True}}
)
async def api_lnwidget_create_invoice(lnwidget_id):
    lnwidget = await get_lnwidget(lnwidget_id)

    if not lnwidget:
        return jsonify({"message": "lnwidget does not exist."}), HTTPStatus.NOT_FOUND

    try:
        payment_hash, payment_request = await create_invoice(
            wallet_id=lnwidget.wallet,
            amount=g.data["amount"],
            memo=f"{lnwidget.name}",
            extra={"tag": "lnwidget"},
        )
    except Exception as e:
        return jsonify({"message": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

    return (
        jsonify({"payment_hash": payment_hash, "payment_request": payment_request}),
        HTTPStatus.CREATED,
    )


@lnwidget_ext.route("/api/v1/lnwidgets/<lnwidget_id>/invoices/<payment_hash>", methods=["GET"])
async def api_lnwidget_check_invoice(lnwidget_id, payment_hash):
    lnwidget = await get_lnwidget(lnwidget_id)

    if not lnwidget:
        return jsonify({"message": "lnwidget does not exist."}), HTTPStatus.NOT_FOUND

    try:
        status = await check_invoice_status(lnwidget.wallet, payment_hash)
        is_paid = not status.pending
    except Exception as exc:
        print(exc)
        return jsonify({"paid": False}), HTTPStatus.OK

    if is_paid:
        wallet = await get_wallet(lnwidget.wallet)
        payment = await wallet.get_payment(payment_hash)
        await payment.set_pending(False)

        return jsonify({"paid": True}), HTTPStatus.OK

    return jsonify({"paid": False}), HTTPStatus.OK
