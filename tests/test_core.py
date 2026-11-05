import io

import numpy as np
import pytest
from PIL import Image

from steganography import (
    DEFAULT_MESSAGE,
    MessageTooLargeError,
    NoHiddenMessageError,
    capacity,
    decrypt,
    encrypt,
)


@pytest.fixture
def cover() -> Image.Image:
    rng = np.random.default_rng(0)
    return Image.fromarray(rng.integers(0, 256, (64, 64, 3), dtype=np.uint8), mode="RGB")


def save_and_reload(image: Image.Image, fmt: str = "PNG", **options) -> Image.Image:
    buffer = io.BytesIO()
    image.save(buffer, format=fmt, **options)
    buffer.seek(0)
    return Image.open(buffer)


def test_default_message_round_trip(cover):
    assert decrypt(save_and_reload(encrypt(cover))) == "welcome steganography!"


def test_custom_and_unicode_messages(cover):
    for message in ["", "hello", "Ünïcödé ✓ 日本語"]:
        assert decrypt(encrypt(cover, message)) == message


def test_only_least_significant_bits_change(cover):
    before = np.asarray(cover, dtype=np.int16)
    after = np.asarray(encrypt(cover), dtype=np.int16)
    assert np.abs(before - after).max() <= 1


def test_capacity_is_enforced(cover):
    largest = "x" * capacity(cover)
    assert decrypt(encrypt(cover, largest)) == largest
    with pytest.raises(MessageTooLargeError):
        encrypt(cover, largest + "x")


def test_alpha_channel_is_preserved():
    rgba = Image.fromarray(np.full((32, 32, 4), 128, dtype=np.uint8), mode="RGBA")
    result = encrypt(rgba, DEFAULT_MESSAGE)
    assert result.mode == "RGBA"
    assert np.array_equal(np.asarray(result)[..., 3], np.asarray(rgba)[..., 3])
    assert decrypt(result) == DEFAULT_MESSAGE


def test_plain_image_has_no_message(cover):
    with pytest.raises(NoHiddenMessageError):
        decrypt(cover)


def test_jpeg_destroys_the_message(cover):
    with pytest.raises(NoHiddenMessageError):
        decrypt(save_and_reload(encrypt(cover), "JPEG", quality=95))
