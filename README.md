# LSB Steganography

Hide text inside an image using **least-significant-bit (LSB) steganography**. The image looks exactly the same, but carries a hidden message.

```python
from steganography import encrypt, decrypt

encrypt("cover.png", "welcome steganography!").save("secret.png")
decrypt("secret.png")   # 'welcome steganography!'
```

## How it works

Every pixel has red, green and blue values from 0 to 255. Changing the **lowest bit** of a value moves it by at most 1, which the eye can't see. Each pixel can therefore carry 3 bits of the message.

```
pixel value   1011010[0]  →  1011010[1]     (148 → 149)
                      ▲
            one bit of the message
```

The message is written into the pixels in order:

```
"STEG" (4 bytes) ‖ length (4 bytes) ‖ message (UTF-8)
```

The `STEG` marker lets `decrypt` tell whether an image contains a message, and the length says how many bytes to read.

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Run the example

```bash
python examples/example.py
```

```
Cover image : cover.png (239,992 bytes of capacity)
Message     : welcome steganography!
Saved       : examples/output/secret.png
Decrypted   : welcome steganography!
Changed     : 122 of 1,920,000 colour values, by at most 1
```

### Command line

```bash
steganography encrypt examples/cover.png secret.png          # hides "welcome steganography!"
steganography encrypt examples/cover.png secret.png -m "hi"  # hides your own text
steganography decrypt secret.png
steganography capacity examples/cover.png
```

### Run the tests

```bash
pytest
```

## API

| Function | Description |
| --- | --- |
| `encrypt(image, message="welcome steganography!")` | Hides `message` in the image and returns a new `PIL.Image` |
| `decrypt(image)` | Returns the hidden message as a string |
| `capacity(image)` | Largest message, in bytes, that the image can hold |

`image` can be a file path or a `PIL.Image`. Errors: `MessageTooLargeError` and `NoHiddenMessageError`, both subclasses of `SteganographyError`.

## Notes

- **Save as PNG.** JPEG and other lossy formats change pixel values and destroy the message.
- The alpha (transparency) channel is never modified.
- An 800×800 image holds about 234 KB of text.
- Despite the function names, this hides the message rather than encrypting it: anyone who knows the technique can read it.

## Project structure

```
steganography/
  core.py       encrypt, decrypt, capacity
  cli.py        command line
examples/
  example.py    hides "welcome steganography!" in cover.png
  cover.png
tests/
  test_core.py
```
