from typing import Any, Dict, Optional, Type, TypeVar, Union

from dependency_resolution.mocks import MockProvider

TItem = TypeVar("TItem", bound=object)


class AutoWiredCache:
    __instance: Optional["AutoWiredCache"] = None

    @classmethod
    def get_instance(cls, evaluate_lazy: bool = False) -> "AutoWiredCache":
        if cls.__instance is None:
            cls.__instance = cls(evaluate_lazy)
        return cls.__instance

    def __init__(self, evaluate_lazy: bool = False) -> None:
        """
        :param evaluate_lazy: If True, the peer dependencies will be evaluated only when they are requested.
        """
        self.evaluate_lazy = evaluate_lazy
        self.__objects: Dict[Type, Any] = {}
        self.__blueprints: set[Type] = set()
        self.__evaluated_deps: set[Type] = set()

    def __iadd__(self, other: Union[TItem, Type[TItem], MockProvider]) -> "AutoWiredCache":
        if type(other) == MockProvider:
            self.__objects[other.mock_of] = other.mock
            self.__blueprints.add(other.mock_of)
            self.__evaluated_deps.add(other.mock_of)
            return self

        if type(other) == type:
            self.__set_dependency(other)
        else:
            self.__set_instantiated_dependency(other.__class__, other)
        return self

    def __isub__(self, ttype: Type[TItem]) -> "AutoWiredCache":
        self.__del_dependency(ttype)
        return self

    def __del_dependency(self, ttype: Type[TItem]) -> None:
        del self.__objects[ttype]
        self.__blueprints.remove(ttype)
        self.__evaluated_deps.remove(ttype)
        # TODO: Remove all the dependencies from evaluated_deps set that depend on this one

    def __delitem__(self, ttype: Type[TItem]) -> None:
        self.__del_dependency(ttype)

    def __setitem__(self, ttype: Type[TItem], object: TItem) -> None:
        if type(object) == MockProvider:
            if ttype != object.mock_of:
                raise ValueError(f"Mock of type {object.mock_of} cannot be set under type {ttype}")
            self.__objects[object.mock_of] = object.mock
            self.__blueprints.add(object.mock_of)
            self.__evaluated_deps.add(object.mock_of)
            return

        if ttype not in object.__class__.__mro__:
            raise ValueError(f"Object of type {object.__class__} cannot be set under type {ttype}")
        self.__set_instantiated_dependency(ttype, object)

    def __getitem__(self, ttype: Type[TItem]) -> TItem:
        if ttype not in self.__objects:
            return self.__instantiate(ttype)
        return self.__objects[ttype]

    def __set_dependency(self, ttype: Type) -> None:
        if self.evaluate_lazy:
            self.__blueprints.add(ttype)
            return

        self.__evaluate_deps(ttype)
        self.__blueprints.add(ttype)

    def __set_instantiated_dependency(self, ttype: Type, object: Any) -> None:
        self.__objects[ttype] = object
        self.__blueprints.add(ttype)
        self.__evaluated_deps.add(ttype)

    def __evaluate_deps(self, ttype: Type[TItem]) -> None:
        annotations = self.__get_annotes(ttype)

        all_deps = list({*annotations.values()}.difference(self.__evaluated_deps))
        for peer_dep in all_deps:
            if peer_dep not in self.__blueprints:
                raise ValueError(f"Peer dependency {peer_dep} not found for {ttype}")

            self.__evaluated_deps.add(peer_dep)
            new_peer_deps = {*self.__get_annotes(peer_dep).values()}
            all_deps.extend(new_peer_deps.difference(self.__evaluated_deps))

    def __instantiate(self, ttype: Type[TItem]) -> TItem:
        if ttype not in self.__blueprints:
            raise KeyError(ttype)

        self.__evaluate_deps(ttype)

        annotations = self.__get_annotes(ttype)
        initialization_kwargs = {
            field: self.__objects.get(field_type) or self.__instantiate(field_type)
            for field, field_type in annotations.items()
        }
        self.__objects[ttype] = ttype(**initialization_kwargs)
        return self.__objects[ttype]

    @staticmethod
    def __get_annotes(ttype: Type[TItem]) -> Dict[str, Type]:
        return dict(filter(lambda x: x[0] != "return", ttype.__init__.__annotations__.items()))

    @classmethod
    def flush(cls):
        cls.__instance = None
