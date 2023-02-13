# Dependency Resolution

## How to use

### ProviderCache Usage

When autowiring is not required use ProviderCache for a simple implementation.

Because autowiring is not involved there are algorithms to determine the order of initialization. And therefore ProviderCache is faster.

```python
from dependency_resolution import ProviderCache

class Image:
  def __init__(self, file: str):
    self.file = file

class ImageProcessor:
  def __init__(self, image: Image):
    self.image = image

  def sharpen(self):
    pass

def init_image():
  cache = ProviderCache.get_instance()
  cache += Image("image.png")
  # Can also be done like this
  # cache[Image] = Image("image.png")

def init_processor():
  cache = ProviderCache.get_instance()
  cache += ImageProcessor(cache[Image])

def process_image():
  cache = ProviderCache.get_instance()
  processor = cache[ImageProcessor]
  processor.sharpen()

if __name__ == "__main__":
  init_image()
  init_processor()
  process_image()
```

### AutoWiredCache Usage

When autowiring is required use AutoWiredCache.

AutoWiredCaches accept just the types of the dependencies and will automatically resolve them (given required deps are already present in the Cache or can be created using other deps).

```python
from dependency_resolution import AutoWiredCache

class ImageDriver:
  def __init__(self, proc: ImageProcessor, image: Image):
    self.proc = proc
    self.image = image

  def edit_and_save(self):
    pass

def init_image():
  cache = AutoWiredCache.get_instance()
  cache += Image("image.png")
  # Can also be done like this
  # cache[Image] = Image("image.png")

def init_processor_and_driver():
  cache = AutoWiredCache.get_instance()
  cache += ImageProcessor
  cache += ImageDriver

def process_image():
  cache = AutoWiredCache.get_instance()
  driver = cache[ImageDriver]
  driver.edit_and_save()

if __name__ == "__main__":
  init_image()
  init_processor()
  process_image()
```

`AutoWiredContainer` also supports lazy evaluation of dependencies. When a new type is added to the cache, it is not initialized immediately and as a result any missing deps will be ignored at that moment.

Therefore, `init_processor_and_driver` function from the above example can be as follows

```python
def init_processor_and_driver():
  cache = AutoWiredCache.get_instance()
  cache += ImageDriver
  cache += ImageProcessor
```

When the `ImageDriver` object is obtained from the cache (`cache[ImageDriver]`), the `ImageProcessor` object will be created first following which the `ImageDriver` object will be created.

## Future Plans

- [x] Add autowire support
- [ ] Add Providers to pass specific arguments to the constructor
- [ ] Add support for deleting or removing provided instances in both `ProviderCache` and `AutoWiredCache`
