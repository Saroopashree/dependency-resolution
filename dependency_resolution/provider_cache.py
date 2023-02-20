from typing import Any, Dict, Optional, Type, TypeVar, Union

from dependency_resolution.mocks import MockProvider

TItem = TypeVar("TItem", bound=object)


class ProviderCache:
    __instance: Optional["ProviderCache"] = None
    __objects: Dict[Type, Any] = {}

    @classmethod
    def get_instance(cls) -> "ProviderCache":
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def __iadd__(self, other: Union[TItem, MockProvider]) -> "ProviderCache":
        if type(other) == MockProvider:
            self.__objects[other.mock_of] = other.mock
        else:
            self.__objects[other.__class__] = other
        return self

    def __isub__(self, ttype: Type[TItem]) -> "ProviderCache":
        del self.__objects[ttype]
        return self

    def __getitem__(self, ttype: Type[TItem]) -> TItem:
        return self.__objects[ttype]

    def __setitem__(self, ttype: Type[TItem], object: Union[TItem, MockProvider]) -> None:
        if type(object) == MockProvider:
            if ttype != object.mock_of:
                raise ValueError(f"Mock of type {object.mock_of} cannot be set under type {ttype}")
            self.__objects[ttype] = object.mock
            return

        if ttype not in object.__class__.__mro__:
            raise ValueError(f"Object of type {object.__class__} cannot be set under type {ttype}")
        self.__objects[ttype] = object

    def __delitem__(self, ttype: Type[TItem]) -> None:
        del self.__objects[ttype]

    @classmethod
    def flush(cls):
        cls.__instance = None
        cls.__objects = {}
