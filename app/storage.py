import os
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel

from app.view_models import AddTransactionModel, ViewTransaction


class StorageTransaction(BaseModel):
    date: datetime
    payer: str
    participants: dict[str, float]
    user_debts: dict[str, str]
    commentary: str

    def format_participants(self) -> str:
        return " | \n".join(
            (f"{name}: {value}" for name, value in self.participants.items())
        )

    def sum(self) -> float:
        return sum(self.participants.values())

    def to_view(self, uid: int) -> ViewTransaction:
        return ViewTransaction(
            uid=uid,
            date=format_date(self.date),
            payer=self.payer,
            participants=self.format_participants(),
            commentary=self.commentary,
            sum=self.sum(),
        )


def format_date(date: datetime) -> str:
    return f"{date.year} {date.month} {date.day} {date.hour}:{date.minute}"


class StorageUser(BaseModel):
    name: str


class StorageRoom(BaseModel):
    name: str
    transactions: list[StorageTransaction]
    users: list[StorageUser]


@dataclass
class Storage:
    rooms: dict[str, StorageRoom]
    dir_path: str

    @classmethod
    def load_from_dir(cls, dir_path: str) -> "Storage":
        rooms = {}
        for room_file in os.listdir(dir_path):
            room_id, room_ext = os.path.splitext(room_file)
            if room_ext != ".rooom":
                continue
            with open(os.path.join(dir_path, room_file), "r") as f:
                rooms[room_id] = StorageRoom.model_validate_json(f.read())
        return cls(rooms, dir_path)

    def get_room(self, room_id: str) -> StorageRoom | None:
        return self.rooms.get(room_id)

    def save_transaction(
        self,
        room_id: str,
        transaction: AddTransactionModel,
        transaction_id: int | None = None,
    ) -> None:
        storage_transaction = StorageTransaction(
            date=datetime.now(tz=ZoneInfo("Europe/Moscow")),
            payer=transaction.payer,
            participants={
                name: eval(raw_debt)
                for name, raw_debt in transaction.user_debts.items()
            },
            user_debts=transaction.user_debts,
            commentary=transaction.commentary,
        )
        transactions = self.rooms[room_id].transactions
        if transaction_id:
            transactions[transaction_id] = storage_transaction
        else:
            transactions.append(storage_transaction)
        self.save_room(room_id)

    def save_room(self, room_id: str):
        room_json = self.rooms[room_id].model_dump_json(indent=2)
        with open(os.path.join(self.dir_path, f"{room_id}.rooom"), "w+") as f:
            f.write(room_json)

    def delete_transaction(self, room_id: str, transaction_id: int): 
        self.rooms[room_id].transactions.pop(transaction_id)
        self.save_room(room_id)
