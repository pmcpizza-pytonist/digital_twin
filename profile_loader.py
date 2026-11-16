"""
Loading the twin's profile, with optional encryption.

* Local development: the plain documents in me/ are read directly.
* Public deployment: me/ is NOT uploaded. Instead, `python encrypt_profile.py`
  extracts the text from me/, removes phone numbers, and encrypts it into
  profile.enc with a secret key (PROFILE_KEY). Only profile.enc is published;
  the app decrypts it in memory at startup using PROFILE_KEY, which lives in
  the hosting platform's secrets, never in the code.
"""

import os
import re
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from pypdf import PdfReader

BASE_DIR = Path(__file__).parent
ME_DIR = BASE_DIR / "me"
ENCRYPTED_PROFILE = BASE_DIR / "profile.enc"

PHONE_RE = re.compile(r"\+\d{1,3}[\s\-]?\d{1,3}[\s\-]?\d{3}[\s\-]?\d{3,4}|\b0\d{1,2}-?\d{7}\b")


def redact(text: str) -> str:
    """Remove phone numbers so the public twin never hands them out."""
    return PHONE_RE.sub("[phone removed]", text)


def read_document(path: Path) -> str:
    """Extract plain text from a PDF, DOCX, TXT or MD file."""
    suffix = path.suffix.lower()
    try:
        if suffix == ".pdf":
            reader = PdfReader(str(path))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        if suffix == ".docx":
            from docx import Document  # python-docx

            doc = Document(str(path))
            return "\n".join(p.text for p in doc.paragraphs)
        if suffix in {".txt", ".md"}:
            return path.read_text(encoding="utf-8")
    except Exception as exc:  # a broken file shouldn't take the site down
        print(f"[warn] Could not read {path.name}: {exc}")
    return ""


def load_plain_profile() -> str:
    """Concatenate every readable document in me/ into one context block."""
    sections = []
    for path in sorted(ME_DIR.glob("*")):
        if not path.is_file() or path.name.startswith(".") or path.name.lower() == "readme.md":
            continue
        text = redact(read_document(path)).strip()
        if text:
            title = path.stem.replace("_", " ").replace("-", " ").title()
            sections.append(f"### {title} (from {path.name})\n\n{text}")
            print(f"[info] Loaded {path.name} ({len(text):,} characters)")
    return "\n\n".join(sections)


def encrypt_text(text: str, key: str) -> bytes:
    return Fernet(key.encode()).encrypt(text.encode("utf-8"))


def decrypt_text(token: bytes, key: str) -> str:
    return Fernet(key.encode()).decrypt(token).decode("utf-8")


def load_profile() -> str:
    """Prefer the encrypted profile when a key is configured; otherwise read me/."""
    key = os.getenv("PROFILE_KEY", "").strip()
    if key and ENCRYPTED_PROFILE.exists():
        try:
            text = decrypt_text(ENCRYPTED_PROFILE.read_bytes(), key)
            print(f"[info] Loaded encrypted profile ({len(text):,} characters)")
            return text
        except (InvalidToken, ValueError):
            print("[error] PROFILE_KEY does not match profile.enc - falling back to me/.")
    text = load_plain_profile()
    if not text:
        print("[warn] No profile found (no readable profile.enc and nothing in me/).")
    return text
