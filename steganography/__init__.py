"""
LSB image steganography: hide text inside a picture.

    >>> from steganography import encrypt, decrypt
    >>> encrypt("photo.png", "welcome steganography!").save("secret.png")
    >>> decrypt("secret.png")
    'welcome steganography!'
"""

from .core import (
    DEFAULT_MESSAGE,
    MessageTooLargeError,
    NoHiddenMessageError,
    SteganographyError,
    capacity,
    decrypt,
    encrypt,
)

__version__ = "1.0.0"

__all__ = [
    "DEFAULT_MESSAGE",
    "MessageTooLargeError",
    "NoHiddenMessageError",
    "SteganographyError",
    "capacity",
    "decrypt",
    "encrypt",
]
