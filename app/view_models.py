import enum
from types import EllipsisType

from pydantic import BaseModel, create_model


class ViewTransaction(BaseModel):
    uid: int
    date: str
    payer: str
    participants: str
    commentary: str
    sum: float


class ViewUser(BaseModel):
    name: str
    profit: float


class AddTransactionModel(BaseModel):
    commentary: str
    payer: str
    user_debts: dict[str, str]

class PreTransactionModel(BaseModel):
    sum: float


def create_input_form_for_users(
    user_debts: list[tuple[str, str]],
    payer: str | EllipsisType = ...,
    commentary: str | EllipsisType = ...,
    sum_value: float = 0.0,
) -> type[BaseModel]:
    Payer = enum.Enum("Payer", {name: name for name, _ in user_debts})
    UserDebts = create_model(
        "UserDebts",
        **{
            name: (str, f"{sum_value} / {len(user_debts)}" if sum_value else raw_debt)  # type: ignore
            for name, raw_debt in user_debts
        }
    )
    return create_model(
        "AddTransactionModel",
        commentary=(str, commentary),
        payer=(Payer, payer),
        user_debts=(UserDebts, ...),
    )
