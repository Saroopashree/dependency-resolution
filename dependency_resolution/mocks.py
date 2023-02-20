from typing import Any, Type


class MockProvider:
    def __init__(self, mock: Any, mock_of: Type):
        self.mock = mock
        self.mock_of = mock_of
