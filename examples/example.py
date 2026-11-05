"""
Hide "welcome steganography!" in a photo, then read it back.

    python examples/example.py
"""

from pathlib import Path
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from steganography import DEFAULT_MESSAGE, capacity, decrypt, encrypt  # noqa: E402

HERE = Path(__file__).resolve().parent
COVER = HERE / "cover.png"
OUTPUT = HERE / "output" / "secret.png"


def main() -> None:
    OUTPUT.parent.mkdir(exist_ok=True)

    print(f"Cover image : {COVER.name} ({capacity(COVER):,} bytes of capacity)")
    print(f"Message     : {DEFAULT_MESSAGE}")

    encrypt(COVER, DEFAULT_MESSAGE).save(OUTPUT, format="PNG")
    print(f"Saved       : {OUTPUT.relative_to(HERE.parent)}")

    recovered = decrypt(OUTPUT)
    print(f"Decrypted   : {recovered}")
    assert recovered == DEFAULT_MESSAGE

    before = np.asarray(Image.open(COVER).convert("RGB"), dtype=np.int16)
    after = np.asarray(Image.open(OUTPUT).convert("RGB"), dtype=np.int16)
    changed = np.count_nonzero(before != after)
    print(f"Changed     : {changed} of {before.size:,} colour values, by at most {np.abs(before - after).max()}")


if __name__ == "__main__":
    main()
