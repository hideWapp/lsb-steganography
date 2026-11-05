"""Command line: ``steganography <command> …`` or ``python -m steganography``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core import DEFAULT_MESSAGE, SteganographyError, capacity, decrypt, encrypt


def _encrypt(args: argparse.Namespace) -> None:
    output = Path(args.output)
    if output.suffix.lower() != ".png":
        sys.exit("Output must be a .png file: lossy formats such as JPEG destroy the hidden message.")
    encrypt(args.image, args.message).save(output, format="PNG")
    print(f'Hid "{args.message}" in {output}')


def _decrypt(args: argparse.Namespace) -> None:
    print(decrypt(args.image))


def _capacity(args: argparse.Namespace) -> None:
    print(f"{capacity(args.image):,} bytes")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="steganography", description="Hide text inside an image (LSB steganography).")
    commands = parser.add_subparsers(dest="command", required=True)

    p = commands.add_parser("encrypt", help="hide a message in an image")
    p.add_argument("image", help="cover image")
    p.add_argument("output", help="output image (.png)")
    p.add_argument("-m", "--message", default=DEFAULT_MESSAGE, help=f'text to hide (default: "{DEFAULT_MESSAGE}")')
    p.set_defaults(run=_encrypt)

    p = commands.add_parser("decrypt", help="read the hidden message")
    p.add_argument("image")
    p.set_defaults(run=_decrypt)

    p = commands.add_parser("capacity", help="show how much text an image can hold")
    p.add_argument("image")
    p.set_defaults(run=_capacity)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        args.run(args)
    except SteganographyError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0
