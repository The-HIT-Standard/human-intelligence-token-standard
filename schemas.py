# backend/schemas.py

from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Dict
from datetime import datetime

TrainingStatus = Literal["allowed", "prohibited", "restricted", "negotiable"]

class TrainingRestrictions(BaseModel):
    commercial: TrainingStatus = "allowed"
    model_types: List[str] = Field(default_factory=lambda: ["LLM", "VLM", "AudioGen", "Diffusion"])
    geography: List[str] = Field(default_factory=lambda: ["Global"])

class TrainingRights(BaseModel):
    status: TrainingStatus
    terms_uri: Optional[str] = None
    restrictions: TrainingRestrictions = TrainingRestrictions()

class CreatorLinkedAccount(BaseModel):
    platform: str
    url: str
    verified: bool = False

class Creator(BaseModel):
    name: str
    identity_type: Literal["self", "platform", "verified_entity"] = "self"
    linked_accounts: List[CreatorLinkedAccount] = Field(default_factory=list)

class RightsHolder(BaseModel):
    name: str
    entity_type: Literal["individual", "organization"] = "individual"
    contact_uri: Optional[str] = None

class ContentMetadata(BaseModel):
    title: str
    type: Literal["video", "audio", "image", "text", "code", "dataset", "mixed"] = "mixed"
    hash_sha256: str
    hash_blake3: str
    perceptual_hash: Optional[str] = None
    source_url: Optional[str] = None
    file_format: Optional[str] = None
    creation_timestamp: datetime

class Attestation(BaseModel):
    statement: str
    signature: Optional[str] = None
    timestamp: datetime

class BlockchainInfo(BaseModel):
    commitment_hash: Optional[str] = None
    chain: Literal["ethereum", "polygon", "solana", "none"] = "none"
    transaction_id: Optional[str] = None

class Versioning(BaseModel):
    version: int = 1
    previous_version: Optional[str] = None
    change_log: Optional[str] = None

class HitRecordOut(BaseModel):
    hit_version: str
    hit_id: str
    creator: Creator
    rights_holder: RightsHolder
    content: ContentMetadata
    training_rights: TrainingRights
    attestation: Attestation
    blockchain: BlockchainInfo
    versioning: Versioning

    class Config:
        orm_mode = True

# Request models

class GenerateHitRequest(BaseModel):
    creator_name: str
    rights_holder_name: str
    identity_type: Literal["self", "platform", "verified_entity"] = "self"
    title: str
    content_type: Literal["video", "audio", "image", "text", "code", "dataset", "mixed"] = "mixed"
    rights_status: TrainingStatus
    commercial_status: TrainingStatus = "allowed"
    terms_uri: Optional[str] = None
    model_types: List[str] = Field(default_factory=lambda: ["LLM", "VLM", "AudioGen", "Diffusion"])
    geography: List[str] = Field(default_factory=lambda: ["Global"])
    source_url: Optional[str] = None
    file_format: Optional[str] = None

class LookupResult(BaseModel):
    match: bool
    hit_id: Optional[str] = None
    rights_status: Optional[TrainingStatus] = None
    rights_summary: Optional[str] = None

class BatchFileHash(BaseModel):
    sha256: str

class BatchLookupRequest(BaseModel):
    files: List[BatchFileHash]

class BatchLookupResponseItem(BaseModel):
    sha256: str
    match: bool
    hit_id: Optional[str] = None
    rights_status: Optional[TrainingStatus] = None

class BatchLookupResponse(BaseModel):
    results: List[BatchLookupResponseItem]
