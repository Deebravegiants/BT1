# Q2359: set_contact_debug_interval: verification bypass

## Question
In `gossip/src/cluster_info.rs`, can an unprivileged attacker who can send a payload with forged or malformed proof/signature `set_contact_debug_interval` (near line 255) be satisfied with attacker-authored data that bypasses or short-circuits signature/Merkle/shred verification, breaking the invariant that only authority/leader-signed and proof-valid payloads are accepted, corrupting the signature / Merkle-proof / shred verification result treated as valid?

## Target
- File/function: `gossip/src/cluster_info.rs` :: `set_contact_debug_interval` (around line 255)
- Entrypoint: Gossip protocol ingest (CRDS push/pull over UDP) — attacker can send a payload with forged or malformed proof/signature
- Attacker controls: gossip message bytes, CRDS values, wallclock, and pull-request filters
- Exploit idea: Can `set_contact_debug_interval` (near line 255) be satisfied with attacker-authored data that bypasses or short-circuits signature/merkle/shred verification, so that the signature / Merkle-proof / shred verification result treated as valid is set to an attacker-chosen or inconsistent value.
- Invariant to test: only authority/leader-signed and proof-valid payloads are accepted
- Expected Immunefi impact: Critical. Signature, shred, or Merkle-proof verification can be bypassed, short-circuited, or satisfied with attacker-chosen data, letting unsigned or attacker-authored payloads be treated as leader- or authority-signed.
- Fast validation: add a focused Rust unit/fuzz test on `set_contact_debug_interval` in `gossip/src/cluster_info.rs` asserting a forged proof/signature is rejected.
