# Q1658: prune_expected_ping_responses: resource starvation

## Question
In `core/src/repair/block_id_repair_service.rs`, can an unprivileged attacker who can flood the public entrypoint with unprivileged traffic unprivileged traffic through `prune_expected_ping_responses` (near line 219) monopolize connection slots/bandwidth/scheduler time and starve honest peers, breaking the invariant that honest peers keep a fair share of connection/bandwidth/scheduler resources, corrupting the connection-slot / bandwidth / scheduler share left for honest peers?

## Target
- File/function: `core/src/repair/block_id_repair_service.rs` :: `prune_expected_ping_responses` (around line 219)
- Entrypoint: Repair request/response ingest (serve_repair / ancestor_hashes) — attacker can flood the public entrypoint with unprivileged traffic
- Attacker controls: repair request bytes, nonces, slot/index requests, and repair peer responses
- Exploit idea: Can unprivileged traffic through `prune_expected_ping_responses` (near line 219) monopolize connection slots/bandwidth/scheduler time and starve honest peers, so that the connection-slot / bandwidth / scheduler share left for honest peers is set to an attacker-chosen or inconsistent value.
- Invariant to test: honest peers keep a fair share of connection/bandwidth/scheduler resources
- Expected Immunefi impact: High. Unprivileged transaction, gossip, or QUIC traffic can starve honest peers of connection slots, stake-weighted bandwidth, scheduler capacity, or thread-pool time, blocking legitimate transactions from ever being included.
- Fast validation: add a focused Rust unit/fuzz test on `prune_expected_ping_responses` in `core/src/repair/block_id_repair_service.rs` measuring honest-request latency under an unprivileged flood.
