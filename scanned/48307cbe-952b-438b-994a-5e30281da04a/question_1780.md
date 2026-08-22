# Q1780: disable_pruned_tree_tracking: verification bypass

## Question
In `core/src/repair/repair_weight.rs`, can an unprivileged attacker who can send a payload with forged or malformed proof/signature `disable_pruned_tree_tracking` (near line 92) be satisfied with attacker-authored data that bypasses or short-circuits signature/Merkle/shred verification, breaking the invariant that only authority/leader-signed and proof-valid payloads are accepted, corrupting the signature / Merkle-proof / shred verification result treated as valid?

## Target
- File/function: `core/src/repair/repair_weight.rs` :: `disable_pruned_tree_tracking` (around line 92)
- Entrypoint: Repair request/response ingest (serve_repair / ancestor_hashes) — attacker can send a payload with forged or malformed proof/signature
- Attacker controls: repair request bytes, nonces, slot/index requests, and repair peer responses
- Exploit idea: Can `disable_pruned_tree_tracking` (near line 92) be satisfied with attacker-authored data that bypasses or short-circuits signature/merkle/shred verification, so that the signature / Merkle-proof / shred verification result treated as valid is set to an attacker-chosen or inconsistent value.
- Invariant to test: only authority/leader-signed and proof-valid payloads are accepted
- Expected Immunefi impact: Critical. Signature, shred, or Merkle-proof verification can be bypassed, short-circuited, or satisfied with attacker-chosen data, letting unsigned or attacker-authored payloads be treated as leader- or authority-signed.
- Fast validation: add a focused Rust unit/fuzz test on `disable_pruned_tree_tracking` in `core/src/repair/repair_weight.rs` asserting a forged proof/signature is rejected.
