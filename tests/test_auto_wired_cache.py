from unittest import TestCase

from dependency_resolution import AutoWiredCache
from dependency_resolution.mocks import MockProvider


class Image:
    def __init__(self, file: str) -> None:
        self.file = file


class RGBImage(Image):
    ...


class ImageProcessor:
    def __init__(self, image: Image) -> None:
        self.image = image


class ImageDriver:
    def __init__(self, proc: ImageProcessor, image: Image) -> None:
        self.proc = proc
        self.image = image


class TestAutoWiredCache(TestCase):
    def setUp(self) -> None:
        AutoWiredCache.flush()

    def test_add_instance_dep_by_addition_assignment(self):
        def func1():
            cache = AutoWiredCache.get_instance()
            cache += Image("image.png")

        func1()

        cache = AutoWiredCache.get_instance()

        assert cache.get_instance() is cache
        assert type(cache[Image]) == Image
        assert cache[Image].file == "image.png"

    def test_add_instance_dep_by_setitem(self):
        def func1():
            cache = AutoWiredCache.get_instance()
            cache[Image] = Image("image.png")

        func1()

        cache = AutoWiredCache.get_instance()

        assert type(cache[Image]) == Image
        assert cache[Image].file == "image.png"

    def test_add_dep_by_addition_assignment(self):
        def func1():
            cache = AutoWiredCache.get_instance()
            cache += Image("image.png")
            cache += ImageProcessor

        func1()

        cache = AutoWiredCache.get_instance()

        assert type(cache[Image]) == Image
        assert type(cache[ImageProcessor]) == ImageProcessor
        assert cache[ImageProcessor].image == cache[Image]

    def test_failure_on_missing_peer(self):
        def func1():
            cache = AutoWiredCache.get_instance()
            cache += ImageProcessor

        with self.assertRaises(ValueError) as e:
            func1()

        assert (
            e.exception.args[0]
            == "Peer dependency <class 'tests.test_auto_wired_cache.Image'> not found for <class 'tests.test_auto_wired_cache.ImageProcessor'>"
        )

    def test_failure_add_instance_dep_by_setitem_with_wrong_type(self):
        def func1():
            cache = AutoWiredCache.get_instance()
            cache[Image] = 1

        with self.assertRaises(ValueError) as e:
            func1()

        assert (
            e.exception.args[0]
            == "Object of type <class 'int'> cannot be set under type <class 'tests.test_auto_wired_cache.Image'>"
        )

    def test_lazy_evaluation_failure_missing_object(self):
        def func1():
            cache = AutoWiredCache.get_instance(evaluate_lazy=True)
            cache += Image("image.png")

        func1()

        cache = AutoWiredCache.get_instance()
        assert type(cache[Image]) == Image
        with self.assertRaises(KeyError) as e:
            cache[ImageProcessor]

        assert e.exception.args[0] == ImageProcessor

    def test_lazy_evaluation_failure_missing_dep(self):
        def func1():
            cache = AutoWiredCache.get_instance(evaluate_lazy=True)
            cache += Image("image.png")
            cache += ImageDriver

        func1()

        cache = AutoWiredCache.get_instance()
        assert type(cache[Image]) == Image
        with self.assertRaises(ValueError) as e:
            cache[ImageDriver]

        assert (
            e.exception.args[0]
            == "Peer dependency <class 'tests.test_auto_wired_cache.ImageProcessor'> not found for <class 'tests.test_auto_wired_cache.ImageDriver'>"
        )

    def test_dep_evaluation_alg(self):
        def func1():
            cache = AutoWiredCache.get_instance(evaluate_lazy=True)
            cache += Image("image.png")
            cache += ImageProcessor
            cache += ImageDriver

        func1()

        cache = AutoWiredCache.get_instance()
        driver = cache[ImageDriver]
        assert type(driver) == ImageDriver
        assert driver.image == cache[Image]
        assert driver.proc == cache[ImageProcessor]

    def test_remove_dep_by_subtract_assignment(self):
        cache = AutoWiredCache.get_instance()
        cache += Image("image.png")

        cache -= Image

        with self.assertRaises(KeyError) as e:
            cache[Image]
        assert e.exception.args[0] == Image

    def test_remove_dep_by_del_keyword(self):
        cache = AutoWiredCache.get_instance()
        cache += Image("image.png")

        del cache[Image]

        with self.assertRaises(KeyError) as e:
            cache[Image]
        assert e.exception.args[0] == Image

    def test_add_mock_by_add_assignment(self):
        class MockImage:
            ...

        cache = AutoWiredCache.get_instance()
        mock_image = MockImage()
        cache += MockProvider(mock_image, mock_of=Image)

        assert cache[Image] == mock_image

    def test_add_mock_by_setitem(self):
        class MockImage:
            ...

        cache = AutoWiredCache.get_instance()
        mock_image = MockImage()
        cache[Image] = MockProvider(mock_image, mock_of=Image)

        assert cache[Image] == mock_image

    def test_add_mock_failure_wrong_type(self):
        class DiskImage:
            ...

        class MockImage:
            ...

        cache = AutoWiredCache.get_instance()

        with self.assertRaises(ValueError) as e:
            cache[DiskImage] = MockProvider(MockImage(), mock_of=Image)

        assert (
            e.exception.args[0]
            == f"Mock of type <class 'tests.test_auto_wired_cache.Image'> cannot be set under type {DiskImage}"
        )

    def test_resolve_dependency_using_mocks(self):
        class MockImage:
            ...

        class MockImageProcessor:
            ...

        cache = AutoWiredCache.get_instance()
        mock_image, mock_image_proc = MockImage(), MockImageProcessor()
        cache += MockProvider(mock_image, mock_of=Image)
        cache += MockProvider(mock_image_proc, mock_of=ImageProcessor)
        cache += ImageDriver

        assert type(cache[ImageDriver]) == ImageDriver
        assert cache[ImageDriver].image == mock_image
        assert cache[ImageDriver].proc == mock_image_proc
