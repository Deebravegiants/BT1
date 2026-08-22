# Q2066: new_with_client: verification bypass

## Question
In `core/src/tpu.rs`, can an unprivileged attacker who can send a payload with forged or malformed proof/signature `new_with_client` (near line 118) be satisfied with attacker-authored data that bypasses or short-circuits signature/Merkle/shred verification, breaking the invariant that only authority/leader-signed and proof-valid payloads are accepted, corrupting the signature / Merkle-proof / shred verification result treated as valid?

## Target
- File/function: `core/src/tpu.rs` :: `new_with_client` (around line 118)
- Entrypoint: TPU/TVU packet fetch and sigverify stage — attacker can send a payload with forged or malformed proof/signature
- Attacker controls: packet batches, signatures, and dedup/shred inputs
- Exploit idea: Can `new_with_client` (near line 118) be satisfied with attacker-authored data that bypasses or short-circuits signature/merkle/shred verification, so that the signature / Merkle-proof / shred verification result treated as valid is set to an attacker-chosen or inconsistent value.
- Invariant to test: only authority/leader-signed and proof-valid payloads are accepted
- Expected Immunefi impact: Critical. Signature, shred, or Merkle-proof verification can be bypassed, short-circuited, or satisfied with attacker-chosen data, letting unsigned or attacker-authored payloads be treated as leader- or authority-signed.
- Fast validation: add a focused Rust unit/fuzz test on `new_with_client` in `core/src/tpu.rs` asserting a forged proof/signature is rejected.
