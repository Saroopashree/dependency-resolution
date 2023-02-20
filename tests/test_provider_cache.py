from unittest import TestCase

from dependency_resolution import ProviderCache
from dependency_resolution.mocks import MockProvider


class Image:
    def __init__(self, file: str) -> None:
        self.file = file


class RGBImage(Image):
    ...


class TestProviderCache(TestCase):
    def setUp(self) -> None:
        ProviderCache.flush()

    def test_add_dependency_by_addition_assignment(self):
        def func1():
            cache = ProviderCache.get_instance()
            cache += Image("image.png")

        func1()

        cache = ProviderCache.get_instance()

        assert cache.get_instance() is cache
        assert type(cache[Image]) == Image
        assert cache[Image].file == "image.png"

    def test_add_dependency_by_setitem(self):
        def func1():
            cache = ProviderCache.get_instance()
            cache[Image] = Image("image.png")

        func1()

        cache = ProviderCache.get_instance()

        assert type(cache[Image]) == Image
        assert cache[Image].file == "image.png"

    def test_add_dependency_by_setitem_with_wrong_type(self):
        def func1():
            cache = ProviderCache.get_instance()
            cache[Image] = 1

        with self.assertRaises(ValueError) as e:
            func1()

        assert (
            e.exception.args[0]
            == "Object of type <class 'int'> cannot be set under type <class 'tests.test_provider_cache.Image'>"
        )

    def test_add_dependency_under_parent_class(self):
        def func1():
            cache = ProviderCache.get_instance()
            cache[Image] = RGBImage("image.png")

        func1()

        cache = ProviderCache.get_instance()
        assert type(cache[Image]) == RGBImage
        assert cache[Image].file == "image.png"

    def test_override_added_dependency(self):
        def func1():
            cache = ProviderCache.get_instance()
            cache[Image] = Image("image.png")

        func1()

        def func2():
            cache = ProviderCache.get_instance()
            cache[Image] = Image("image2.png")

        func2()

        cache = ProviderCache.get_instance()

        assert type(cache[Image]) == Image
        assert cache[Image].file == "image2.png"

    def test_remove_dep_by_subtract_assignment(self):
        cache = ProviderCache.get_instance()
        cache += Image("image.png")

        cache -= Image

        with self.assertRaises(KeyError) as e:
            cache[Image]
        assert e.exception.args[0] == Image

    def test_remove_dep_by_del_keyword(self):
        cache = ProviderCache.get_instance()
        cache += Image("image.png")

        del cache[Image]

        with self.assertRaises(KeyError) as e:
            cache[Image]
        assert e.exception.args[0] == Image

    def test_add_mock_by_add_assignment(self):
        class MockImage:
            ...

        cache = ProviderCache.get_instance()
        mock_image = MockImage()
        cache += MockProvider(mock_image, mock_of=Image)

        assert type(cache[Image]) == MockImage
        assert cache[Image] == mock_image

    def test_add_mock_by_setitem(self):
        class MockImage:
            ...

        cache = ProviderCache.get_instance()
        mock_image = MockImage()
        cache[Image] = MockProvider(mock_image, mock_of=Image)

        assert type(cache[Image]) == MockImage
        assert cache[Image] == mock_image

    def test_add_mock_failure_wrong_type(self):
        class DiskImage:
            ...

        class MockImage:
            ...

        cache = ProviderCache.get_instance()

        with self.assertRaises(ValueError) as e:
            cache[DiskImage] = MockProvider(MockImage(), mock_of=Image)

        assert (
            e.exception.args[0]
            == f"Mock of type <class 'tests.test_provider_cache.Image'> cannot be set under type {DiskImage}"
        )

    def test_override_by_mock(self):
        class MockImage:
            ...

        cache = ProviderCache.get_instance()
        cache += Image("image.png")

        assert type(cache[Image]) == Image

        mock_image = MockImage()
        cache += MockProvider(mock_image, mock_of=Image)

        assert type(cache[Image]) == MockImage
        assert cache[Image] == mock_image
