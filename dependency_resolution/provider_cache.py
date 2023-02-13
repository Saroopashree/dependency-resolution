from typing import Optional, Type, TypeVar

TItem = TypeVar("TItem")


class ProviderCache:
    __instance: Optional["ProviderCache"] = None
    __objects: dict[Type[TItem], TItem] = {}

    @classmethod
    def get_instance(cls) -> "ProviderCache":
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def __iadd__(self, other: TItem) -> "ProviderCache":
        self.__objects[other.__class__] = other
        return self

    def __getitem__(self, type: Type[TItem]) -> TItem:
        return self.__objects[type]

    def __setitem__(self, type: Type[TItem], object: TItem) -> None:
        if type not in object.__class__.__mro__:
            raise ValueError(f"Provided object is not of type {type.__name__} ({type})")
        self.__objects[type] = object
