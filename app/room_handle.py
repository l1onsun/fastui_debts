from dataclasses import dataclass

from app.storage import Storage, StorageTransaction, StorageUser
from app.view_models import AddTransactionModel, ViewTransaction, ViewUser


@dataclass
class RoomHandle:
    room_id: str
    name: str
    transactions: list[StorageTransaction]
    users: list[StorageUser]
    storage: Storage

    def list_transactions(self) -> list[ViewTransaction]:
        return [tr.to_view(i) for i, tr in enumerate(self.transactions)]

    def list_users(self) -> list[ViewUser]:
        profit_by_user = self._calc_user_profits()
        return [
            ViewUser(name=user.name, profit=profit_by_user[user.name])
            for user in self.users
        ]

    def _calc_user_profits(self) -> dict[str, float]:
        profit = {user.name: 0.0 for user in self.users}
        for transaction in self.transactions:
            for name, debt in transaction.participants.items():
                profit[name] += debt
            profit[transaction.payer] -= transaction.sum()
        return profit

    def save_transaction(
        self, transaction: AddTransactionModel, transaction_id: int | None = None
    ) -> None:
        self.storage.save_transaction(self.room_id, transaction, transaction_id)

    def delete_transaction(self, transaction_id: int):
        self.storage.delete_transaction(self.room_id, transaction_id)
