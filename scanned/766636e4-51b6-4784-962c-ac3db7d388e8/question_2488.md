# Q2488: snapshot_from_contact_info_preserves_pubkey_and_versions: verification bypass

## Question
In `gossip/src/contact_info_notifier.rs`, can an unprivileged attacker who can send a payload with forged or malformed proof/signature `snapshot_from_contact_info_preserves_pubkey_and_versions` (near line 134) be satisfied with attacker-authored data that bypasses or short-circuits signature/Merkle/shred verification, breaking the invariant that only authority/leader-signed and proof-valid payloads are accepted, corrupting the signature / Merkle-proof / shred verification result treated as valid?

## Target
- File/function: `gossip/src/contact_info_notifier.rs` :: `snapshot_from_contact_info_preserves_pubkey_and_versions` (around line 134)
- Entrypoint: Gossip protocol ingest (CRDS push/pull over UDP) — attacker can send a payload with forged or malformed proof/signature
- Attacker controls: gossip message bytes, CRDS values, wallclock, and pull-request filters
- Exploit idea: Can `snapshot_from_contact_info_preserves_pubkey_and_versions` (near line 134) be satisfied with attacker-authored data that bypasses or short-circuits signature/merkle/shred verification, so that the signature / Merkle-proof / shred verification result treated as valid is set to an attacker-chosen or inconsistent value.
- Invariant to test: only authority/leader-signed and proof-valid payloads are accepted
- Expected Immunefi impact: Critical. Signature, shred, or Merkle-proof verification can be bypassed, short-circuited, or satisfied with attacker-chosen data, letting unsigned or attacker-authored payloads be treated as leader- or authority-signed.
- Fast validation: add a focused Rust unit/fuzz test on `snapshot_from_contact_info_preserves_pubkey_and_versions` in `gossip/src/contact_info_notifier.rs` asserting a forged proof/signature is rejected.
