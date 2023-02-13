# Dependency Resolution

## How to use

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
  instance = ProviderCache.get_instance()
  instance += Image("image.png")
  # Can also be done like this
  # instance[Image] = Image("image.png")


def init_processor():
  instance = ProviderCache.get_instance()
  instance += ImageProcessor(instance[Image])


def process_image():
  instance = ProviderCache.get_instance()
  processor = instance[ImageProcessor]
  processor.sharpen()


if __name__ == "__main__":
  init_image()
  init_processor()
  process_image()
```

## Future Plans

- [ ] Add autowire support
- [ ] Add Providers to pass specific arguments to the constructor
