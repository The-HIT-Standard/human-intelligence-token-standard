# backend/app.py

import json
import uuid
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, engine, get_db  # note: no dots
from models import HitRecord
from schemas import (
    TrainingRights,
    TrainingRestrictions,
    Creator,
    RightsHolder,
    ContentMetadata,
    Attestation,
    BlockchainInfo,
    Versioning,
    LookupResult,
    BatchLookupRequest,
    BatchLookupResponse,
    BatchLookupResponseItem,
    HitRecordOut,
)
from hashing import sha256_bytes, blake3_bytes

# create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HIT Standard MVP API", version="1.0.0")

# CORS for local dev / simple front-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_hit_id() -> str:
    return f"HIT-{uuid.uuid4().hex[:12]}"


@app.post("/generate_hit", response_model=HitRecordOut)
async def generate_hit(
    file: UploadFile = File(...),
    creator_name: str = Form(...),
    rights_holder_name: str = Form(...),
    identity_type: str = Form("self"),
    title: str = Form(...),
    content_type: str = Form("mixed"),
    rights_status: str = Form(...),
    commercial_status: str = Form("allowed"),
    terms_uri: str = Form(None),
    source_url: str = Form(None),
    file_format: str = Form(None),
    db: Session = Depends(get_db),
):
    # Read file bytes
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")

    sha256 = sha256_bytes(data)
    blake3 = blake3_bytes(data)

    now = datetime.utcnow()

    training_rights = TrainingRights(
        status=rights_status,
        terms_uri=terms_uri,
        restrictions=TrainingRestrictions(
            commercial=commercial_status,
            model_types=["LLM", "VLM", "AudioGen", "Diffusion"],
            geography=["Global"],
        ),
    )

    creator = Creator(
        name=creator_name,
        identity_type=identity_type,
        linked_accounts=[],
    )

    rights_holder = RightsHolder(
        name=rights_holder_name,
        entity_type="individual",
        contact_uri=None,
    )

    content_meta = ContentMetadata(
        title=title,
        type=content_type,
        hash_sha256=sha256,
        hash_blake3=blake3,
        perceptual_hash=None,
        source_url=source_url,
        file_format=file_format or file.content_type,
        creation_timestamp=now,
    )

    attestation = Attestation(
        statement="I declare that I am the creator or rights holder of this work and have authority to set AI training permissions.",
        signature=None,
        timestamp=now,
    )

    blockchain = BlockchainInfo(
        commitment_hash=None,
        chain="none",
        transaction_id=None,
    )

    versioning = Versioning(
        version=1,
        previous_version=None,
        change_log="Initial HIT creation.",
    )

    hit_id = generate_hit_id()

    hit_json = {
        "hit_version": "1.0",
        "hit_id": hit_id,
        "creator": json.loads(creator.json()),
        "rights_holder": json.loads(rights_holder.json()),
        "content": json.loads(content_meta.json()),
        "training_rights": json.loads(training_rights.json()),
        "attestation": json.loads(attestation.json()),
        "blockchain": json.loads(blockchain.json()),
        "versioning": json.loads(versioning.json()),
    }

    record = HitRecord(
        hit_id=hit_id,
        creator_name=creator_name,
        rights_holder_name=rights_holder_name,
        identity_type=identity_type,
        rights_status=rights_status,
        rights_json=json.dumps(hit_json),
        sha256=sha256,
        blake3=blake3,
        source_filename=file.filename,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return HitRecordOut(**hit_json)


@app.get("/hits/{hit_id}", response_model=HitRecordOut)
def get_hit(hit_id: str, db: Session = Depends(get_db)):
    record = db.query(HitRecord).filter(HitRecord.hit_id == hit_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="HIT not found")
    hit_json = json.loads(record.rights_json)
    return HitRecordOut(**hit_json)


@app.get("/lookup/hash", response_model=LookupResult)
def lookup_by_hash(sha256: str, db: Session = Depends(get_db)):
    record = db.query(HitRecord).filter(HitRecord.sha256 == sha256).first()
    if not record:
        return LookupResult(match=False)
    return LookupResult(
        match=True,
        hit_id=record.hit_id,
        rights_status=record.rights_status,
        rights_summary=f"Training is {record.rights_status} for this work.",
    )


@app.post("/lookup/batch", response_model=BatchLookupResponse)
def lookup_batch(req: BatchLookupRequest, db: Session = Depends(get_db)):
    results = []
    sha_list = [f.sha256 for f in req.files]
    records = (
        db.query(HitRecord)
        .filter(HitRecord.sha256.in_(sha_list))
        .all()
    )
    record_map = {r.sha256: r for r in records}

    for f in req.files:
        r = record_map.get(f.sha256)
        if not r:
            results.append(
                BatchLookupResponseItem(
                    sha256=f.sha256,
                    match=False,
                    hit_id=None,
                    rights_status=None,
                )
            )
        else:
            results.append(
                BatchLookupResponseItem(
                    sha256=f.sha256,
                    match=True,
                    hit_id=r.hit_id,
                    rights_status=r.rights_status,
                )
            )

    return BatchLookupResponse(results=results)
