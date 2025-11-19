# backend/hashing.py

import hashlib

def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

def blake3_bytes(data: bytes) -> str:
    # lightweight fallback if blake3 library isn't installed
    # (you can swap to real blake3 if you install it)
    h = hashlib.blake2s()
    h.update(data)
    return h.hexdigest()
