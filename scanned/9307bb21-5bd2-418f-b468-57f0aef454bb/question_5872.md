# Q5872: with_capacity: wire-parse panic/overflow

## Question
In `turbine/src/addr_cache.rs`, can an unprivileged attacker who can send crafted bytes on the public protocol feeding this parser malformed/truncated attacker bytes reach `with_capacity` (near line 109) and hit a panic, unwrap, overflow, or out-of-range index that aborts the node, breaking the invariant that every length/offset from untrusted bytes is bounds-checked before use, corrupting the length/offset/index derived from attacker bytes before the buffer access?

## Target
- File/function: `turbine/src/addr_cache.rs` :: `with_capacity` (around line 109)
- Entrypoint: Turbine shred broadcast / retransmit and shred sigverify — attacker can send crafted bytes on the public protocol feeding this parser
- Attacker controls: shred bytes, Merkle proofs, fec-set indices, and shred signatures
- Exploit idea: Can malformed/truncated attacker bytes reach `with_capacity` (near line 109) and hit a panic, unwrap, overflow, or out-of-range index that aborts the node, so that the length/offset/index derived from attacker bytes before the buffer access is set to an attacker-chosen or inconsistent value.
- Invariant to test: every length/offset from untrusted bytes is bounds-checked before use
- Expected Immunefi impact: Critical. Malformed, truncated, or adversarially crafted bytes arriving over QUIC/TPU, gossip, shred ingest, repair, or blockstore deserialization reach a panic, unwrap, slice-index, integer overflow, or debug assertion that aborts or wedges the validator process.
- Fast validation: add a focused Rust unit/fuzz test on `with_capacity` in `turbine/src/addr_cache.rs` feeding malformed/truncated bytes and asserting no panic/overflow.
