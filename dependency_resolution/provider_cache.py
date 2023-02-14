from typing import Any, Dict, Optional, Type, TypeVar

TItem = TypeVar("TItem", bound=object)


class ProviderCache:
    __instance: Optional["ProviderCache"] = None
    __objects: Dict[Type, Any] = {}

    @classmethod
    def get_instance(cls) -> "ProviderCache":
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def __iadd__(self, other: TItem) -> "ProviderCache":
        self.__objects[other.__class__] = other
        return self

    def __getitem__(self, ttype: Type[TItem]) -> TItem:
        return self.__objects[ttype]

    def __setitem__(self, ttype: Type[TItem], object: TItem) -> None:
        if ttype not in object.__class__.__mro__:
            raise ValueError(f"Object of type {object.__class__} cannot be set under type {ttype}")
        self.__objects[ttype] = object

    @classmethod
    def flush(cls):
        cls.__instance = None
        cls.__objects = {}
