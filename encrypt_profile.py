"""
Encrypt the documents in me/ into profile.enc for public deployment.

Usage:
    python encrypt_profile.py --new-key   # first time: creates PROFILE_KEY and saves it in .env
    python encrypt_profile.py             # after editing files in me/: re-encrypt with the same key

Publish profile.enc (safe to make public) and set PROFILE_KEY as a secret on
your hosting platform. Never publish me/ or .env.
"""

import argparse
import os
import sys
from pathlib import Path

from cryptography.fernet import Fernet
from dotenv import load_dotenv

from profile_loader import ENCRYPTED_PROFILE, decrypt_text, encrypt_text, load_plain_profile

ENV_FILE = Path(__file__).parent / ".env"


def save_key_to_env(key: str) -> None:
    lines = ENV_FILE.read_text(encoding="utf-8").splitlines() if ENV_FILE.exists() else []
    lines = [line for line in lines if not line.startswith("PROFILE_KEY=")]
    lines.append(f"PROFILE_KEY={key}")
    ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--new-key", action="store_true", help="generate a new PROFILE_KEY and store it in .env")
    args = parser.parse_args()

    load_dotenv(ENV_FILE, override=True)
    key = os.getenv("PROFILE_KEY", "").strip()

    if args.new_key:
        if key:
            answer = input("PROFILE_KEY already exists in .env. Replace it? [y/N] ")
            if answer.strip().lower() != "y":
                sys.exit("Keeping the existing key.")
        key = Fernet.generate_key().decode()
        save_key_to_env(key)
        print("New PROFILE_KEY saved to .env")
    elif not key:
        sys.exit("No PROFILE_KEY found. Run:  python encrypt_profile.py --new-key")

    text = load_plain_profile()
    if not text:
        sys.exit("Nothing to encrypt - put your documents in me/ first.")

    ENCRYPTED_PROFILE.write_bytes(encrypt_text(text, key))
    assert decrypt_text(ENCRYPTED_PROFILE.read_bytes(), key) == text  # round-trip check
    print(f"Encrypted {len(text):,} characters into {ENCRYPTED_PROFILE.name}")
    print("Remember to set the same PROFILE_KEY as a secret on your hosting platform.")


if __name__ == "__main__":
    main()
