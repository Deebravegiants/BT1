# Q2861: set_max_expired_slot: verification bypass

## Question
In `ledger/src/blockstore/blockstore_purge.rs`, can an unprivileged attacker who can send a payload with forged or malformed proof/signature `set_max_expired_slot` (near line 112) be satisfied with attacker-authored data that bypasses or short-circuits signature/Merkle/shred verification, breaking the invariant that only authority/leader-signed and proof-valid payloads are accepted, corrupting the signature / Merkle-proof / shred verification result treated as valid?

## Target
- File/function: `ledger/src/blockstore/blockstore_purge.rs` :: `set_max_expired_slot` (around line 112)
- Entrypoint: Blockstore / shred ingestion and entry replay — attacker can send a payload with forged or malformed proof/signature
- Attacker controls: shred bytes, entry payloads, slot/index fields, and block metadata
- Exploit idea: Can `set_max_expired_slot` (near line 112) be satisfied with attacker-authored data that bypasses or short-circuits signature/merkle/shred verification, so that the signature / Merkle-proof / shred verification result treated as valid is set to an attacker-chosen or inconsistent value.
- Invariant to test: only authority/leader-signed and proof-valid payloads are accepted
- Expected Immunefi impact: Critical. Signature, shred, or Merkle-proof verification can be bypassed, short-circuited, or satisfied with attacker-chosen data, letting unsigned or attacker-authored payloads be treated as leader- or authority-signed.
- Fast validation: add a focused Rust unit/fuzz test on `set_max_expired_slot` in `ledger/src/blockstore/blockstore_purge.rs` asserting a forged proof/signature is rejected.
