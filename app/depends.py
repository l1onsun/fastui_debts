from fastapi import Depends

from app.room_handle import RoomHandle
from app.storage import Storage, StorageRoom


def get_storage() -> Storage:
    return Storage.load_from_dir("./data")
    # return Storage(
    #     rooms={
    #         "1": StorageRoom(
    #             name="Майский трип",
    #             transactions=[
    #                 StorageTransaction(
    #                     date=datetime.now(),
    #                     payer="Pavel",
    #                     participants={"Pavel": 700, "Ilya": 700, "Sultan": 700},
    #                     user_debts={"Pavel": "700", "Ilya": "700", "Sultan": "700"},
    #                     commentary="Такси Нальчик->Пятигорск",
    #                 ),
    #             ],
    #             users=[
    #                 StorageUser(name="Ilya"),
    #                 StorageUser(name="Sultan"),
    #                 StorageUser(name="Pavel"),
    #             ],
    #         )
    #     }
    # )


def get_room_handle(
    room_id: str, storage: Storage = Depends(get_storage)
) -> RoomHandle:
    storage_room: StorageRoom | None = storage.rooms.get(room_id)
    if storage_room:
        return RoomHandle(
            room_id=room_id,
            name=storage_room.name,
            transactions=storage_room.transactions,
            users=storage_room.users,
            storage=storage,
        )
    else:
        return RoomHandle(
            room_id=room_id,
            name="Unknown Room",
            transactions=[],
            users=[],
            storage=storage,
        )
