# Human Intelligence Token (HIT) Standard — MVP

This repository contains the first working MVP implementation of the **Human Intelligence Token (HIT) Standard** — a simple, machine-readable way for human creators to declare authorship and AI training rights for their digital works.

On November 19, 2025, the first HIT was created for a handwritten note that read:

> “Love,  
> Humans”

This repo captures that origin.

---

## What this MVP does

- Lets a creator upload any digital file (image, video, audio, text, etc.)
- Generates cryptographic hashes (SHA-256 + BLAKE-style) as a fingerprint
- Lets the creator declare AI training rights:
  - `allowed`
  - `prohibited`
  - `restricted`
  - `negotiable`
- Returns a full **HIT record** as a JSON document:
  - creator info
  - rights holder
  - content metadata
  - training rights
  - attestation
  - versioning
- Stores the HIT record in a simple SQLite database
- Exposes an API for AI systems to:
  - generate HITs
  - look up rights by hash
  - fetch HIT metadata by HIT ID

This is **not** a platform or a token sale.  
It is a working proof-of-concept for a **rights and provenance standard** for AI training.

---

## Project structure

```text
backend/
  app.py          # FastAPI app and endpoints
  database.py     # SQLite database setup
  models.py       # SQLAlchemy models (HitRecord)
  schemas.py      # Pydantic schemas (HitRecordOut, etc.)
  hashing.py      # File hashing helpers
  config.py       # DB config

frontend/
  index.html      # HIT Generator UI (upload + form)
  style.css       # Basic styling

examples/
  0001_LoveHumans/
    love-humans.jpg      # First content artifact
    HIT-0001.json        # First Human Intelligence Token
