# Q1656: prune_expected_ping_responses: verification bypass

## Question
In `core/src/repair/block_id_repair_service.rs`, can an unprivileged attacker who can send a payload with forged or malformed proof/signature `prune_expected_ping_responses` (near line 219) be satisfied with attacker-authored data that bypasses or short-circuits signature/Merkle/shred verification, breaking the invariant that only authority/leader-signed and proof-valid payloads are accepted, corrupting the signature / Merkle-proof / shred verification result treated as valid?

## Target
- File/function: `core/src/repair/block_id_repair_service.rs` :: `prune_expected_ping_responses` (around line 219)
- Entrypoint: Repair request/response ingest (serve_repair / ancestor_hashes) — attacker can send a payload with forged or malformed proof/signature
- Attacker controls: repair request bytes, nonces, slot/index requests, and repair peer responses
- Exploit idea: Can `prune_expected_ping_responses` (near line 219) be satisfied with attacker-authored data that bypasses or short-circuits signature/merkle/shred verification, so that the signature / Merkle-proof / shred verification result treated as valid is set to an attacker-chosen or inconsistent value.
- Invariant to test: only authority/leader-signed and proof-valid payloads are accepted
- Expected Immunefi impact: Critical. Signature, shred, or Merkle-proof verification can be bypassed, short-circuited, or satisfied with attacker-chosen data, letting unsigned or attacker-authored payloads be treated as leader- or authority-signed.
- Fast validation: add a focused Rust unit/fuzz test on `prune_expected_ping_responses` in `core/src/repair/block_id_repair_service.rs` asserting a forged proof/signature is rejected.
