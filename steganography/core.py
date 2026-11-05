"""
Least-significant-bit (LSB) image steganography.

A message is hidden in the lowest bit of each pixel's red, green and blue
values. Changing that bit moves a colour value by at most 1 out of 255, so
the image looks exactly the same.

Data layout, written into the pixels in scanline order::

    magic "STEG" (4 bytes) ‖ message length (4 bytes, big-endian) ‖ message (UTF-8)

Each pixel carries 3 bits, so an image holds roughly ``width × height × 3 / 8``
bytes. Save the result as PNG — lossy formats such as JPEG destroy the
hidden bits.
"""

from __future__ import annotations

import struct
from pathlib import Path
from typing import Union

import numpy as np
from PIL import Image

DEFAULT_MESSAGE = "welcome steganography!"

MAGIC = b"STEG"
_HEADER = struct.Struct(">4sI")  # magic, message length
CHANNELS = 3  # R, G, B — alpha is never modified

ImageSource = Union[str, Path, Image.Image]


class SteganographyError(Exception):
    """Base class for errors raised by this package."""


class MessageTooLargeError(SteganographyError):
    """The message does not fit in the image."""


class NoHiddenMessageError(SteganographyError):
    """The image does not contain a message written by :func:`encrypt`."""


def _open(source: ImageSource) -> Image.Image:
    image = source if isinstance(source, Image.Image) else Image.open(source)
    has_alpha = "A" in image.getbands() or "transparency" in image.info
    return image.convert("RGBA" if has_alpha else "RGB")


def _rgb_values(image: Image.Image) -> np.ndarray:
    """All R, G, B values of the image as one flat, writable array (alpha excluded)."""
    return np.array(image)[..., :CHANNELS].reshape(-1)


def capacity(source: ImageSource) -> int:
    """Largest message, in bytes, that fits in the image."""
    image = _open(source)
    return max(0, image.width * image.height * CHANNELS // 8 - _HEADER.size)


def encrypt(source: ImageSource, message: str = DEFAULT_MESSAGE) -> Image.Image:
    """Hide ``message`` in the image and return the result.

    Save the returned image as PNG to keep the message intact.
    """
    image = _open(source)
    data = message.encode("utf-8")
    available = capacity(image)
    if len(data) > available:
        raise MessageTooLargeError(f"message is {len(data)} bytes; this image holds at most {available}")

    payload = _HEADER.pack(MAGIC, len(data)) + data
    bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))

    values = _rgb_values(image)
    values[: bits.size] = (values[: bits.size] & 0xFE) | bits  # clear the LSB, then set it

    pixels = np.array(image)
    pixels[..., :CHANNELS] = values.reshape(image.height, image.width, CHANNELS)
    return Image.fromarray(pixels, mode=image.mode)


def decrypt(source: ImageSource) -> str:
    """Read back the message hidden by :func:`encrypt`."""
    values = _rgb_values(_open(source))

    def read(offset: int, count: int) -> bytes:
        start, end = offset * 8, (offset + count) * 8
        if end > values.size:
            raise NoHiddenMessageError("the image is too small to contain a message")
        return np.packbits(values[start:end] & 1).tobytes()

    magic, length = _HEADER.unpack(read(0, _HEADER.size))
    if magic != MAGIC:
        raise NoHiddenMessageError("no hidden message found in this image")
    if length > values.size // 8 - _HEADER.size:
        raise NoHiddenMessageError("hidden message is corrupted")

    try:
        return read(_HEADER.size, length).decode("utf-8")
    except UnicodeDecodeError:
        raise NoHiddenMessageError("hidden message is corrupted") from None
