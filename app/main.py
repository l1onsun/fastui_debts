from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.responses import HTMLResponse
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui import prebuilt_html
from fastui.components.display import DisplayLookup
from fastui.events import GoToEvent, PageEvent
from fastui.forms import fastui_form

from app.depends import get_room_handle
from app.room_handle import RoomHandle
from app.view_models import (
    AddTransactionModel,
    PreTransactionModel,
    ViewTransaction,
    ViewUser,
    create_input_form_for_users,
)

app = FastAPI()
UI_PATH = "room"


@app.get(
    f"/api/{UI_PATH}/{{room_id}}",
    response_model=FastUI,
    response_model_exclude_none=True,
)
def room(room: RoomHandle = Depends(get_room_handle)) -> list[AnyComponent]:
    print(f"Enter Room {room.name}")
    return [
        c.Page(
            components=[
                c.Heading(text=room.name),
                c.Heading(text="Profits", level=3),
                c.Table(
                    data=room.list_users(),
                    columns=[
                        DisplayLookup(field="name"),
                        DisplayLookup(field="profit"),
                    ],
                    data_model=ViewUser,
                ),
                c.Table(
                    data=room.list_transactions(),
                    columns=[
                        DisplayLookup(
                            field="uid",
                            on_click=GoToEvent(
                                url=f"/{UI_PATH}/{room.room_id}/add_transaction?uid={{uid}}"
                            ),
                        ),
                        DisplayLookup(field="date"),
                        DisplayLookup(field="payer"),
                        DisplayLookup(field="participants"),
                        DisplayLookup(field="commentary"),
                        DisplayLookup(field="sum"),
                    ],
                    data_model=ViewTransaction,
                ),
                c.Button(
                    text="New Transaction",
                    on_click=PageEvent(name="modal-form"),
                    # GoToEvent(
                    #     url=f"/{UI_PATH}/{room.room_id}/add_transaction"
                    # ),
                ),
                c.Modal(
                    title="Transaction sum",
                    body=[
                        c.Paragraph(text="Remain 0 if not equal distribution."),
                        c.Form(
                            form_fields=[
                                c.FormFieldInput(
                                    name="sum",
                                    title="Sum",
                                    initial="0",
                                    required=True,
                                ),
                            ],
                            submit_url=f"/api/forms/room/{room.room_id}/pre_new_transaction",
                            footer=[],
                            submit_trigger=PageEvent(name="modal-form-submit"),
                        ),
                    ],
                    footer=[
                        c.Button(
                            text="Cancel",
                            named_style="secondary",
                            on_click=PageEvent(name="modal-form", clear=True),
                        ),
                        c.Button(
                            text="Submit", on_click=PageEvent(name="modal-form-submit")
                        ),
                    ],
                    open_trigger=PageEvent(name="modal-form"),
                ),
            ]
        )
    ]


@app.get(
    f"/api/{UI_PATH}/{{room_id}}/add_transaction",
    response_model=FastUI,
    response_model_exclude_none=True,
)
def add_transaction(
    room: RoomHandle = Depends(get_room_handle), uid: int | None = None, sum: float = 0
) -> list[AnyComponent]:
    print(f"Enter /add transaction/ Room {room.name}")
    transaction = room.transactions[uid] if uid is not None else None
    return [
        c.Page(
            components=[
                c.Heading(text=room.name),
                c.Heading(text="Add/Edit Transaction", level=3),
                c.Button(
                    text="Delete Transaction",
                    on_click=GoToEvent(
                        url=f"/{UI_PATH}/{room.room_id}/delete_transaction?uid={uid}"
                    ),
                ),
                c.ModelForm(
                    model=create_input_form_for_users(
                        (
                            [(user.name, "0") for user in room.list_users()]
                            if transaction is None
                            else list(transaction.user_debts.items())
                        ),
                        payer=transaction.payer if transaction else ...,
                        commentary=transaction.commentary if transaction else ...,
                        sum_value=sum,
                    ),
                    display_mode="page",
                    submit_url=(
                        f"/api/forms/room/{room.room_id}/new_transaction"
                        if uid is None
                        else f"/api/forms/room/{room.room_id}/edit_transaction/{uid}"
                    ),
                ),
            ]
        )
    ]


@app.get(
    f"/api/{UI_PATH}/{{room_id}}/delete_transaction",
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def delete_transaction(
    room: RoomHandle = Depends(get_room_handle),
    uid: int | None = None,
):
    if uid is not None:
        room.delete_transaction(uid)
    return [c.FireEvent(event=GoToEvent(url=f"/{UI_PATH}/{room.room_id}"))]


@app.post(
    "/api/forms/room/{room_id}/new_transaction",
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def new_transaction(
    form: Annotated[AddTransactionModel, fastui_form(AddTransactionModel)],
    room: RoomHandle = Depends(get_room_handle),
):
    print("New transaction for:", room.name)
    room.save_transaction(form)
    return [c.FireEvent(event=GoToEvent(url=f"/{UI_PATH}/{room.room_id}"))]


@app.post(
    "/api/forms/room/{room_id}/pre_new_transaction",
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def pre_transaction(
    form: Annotated[PreTransactionModel, fastui_form(PreTransactionModel)],
    room: RoomHandle = Depends(get_room_handle),
):
    return [
        c.FireEvent(
            event=GoToEvent(
                url=f"/{UI_PATH}/{room.room_id}/add_transaction?sum={form.sum}"
            )
        )
    ]


@app.post(
    "/api/forms/room/{room_id}/edit_transaction/{transaction_id}",
    response_model=FastUI,
    response_model_exclude_none=True,
)
async def edit_transaction(
    form: Annotated[AddTransactionModel, fastui_form(AddTransactionModel)],
    transaction_id: int,
    room: RoomHandle = Depends(get_room_handle),
):
    print("Edit transaction for:", room.name)
    room.save_transaction(form, transaction_id)
    return [c.FireEvent(event=GoToEvent(url=f"/{UI_PATH}/{room.room_id}"))]


@app.get("/{path:path}")
async def html_landing() -> HTMLResponse:
    """Simple HTML page which serves the React app, comes last as it matches all paths."""
    return HTMLResponse(prebuilt_html(title="FastUI Demo"))
