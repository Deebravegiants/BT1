# Q2004: send_votes_to_worker_pool: resource starvation

## Question
In `core/src/sigverify.rs`, can an unprivileged attacker who can flood the public entrypoint with unprivileged traffic unprivileged traffic through `send_votes_to_worker_pool` (near line 96) monopolize connection slots/bandwidth/scheduler time and starve honest peers, breaking the invariant that honest peers keep a fair share of connection/bandwidth/scheduler resources, corrupting the connection-slot / bandwidth / scheduler share left for honest peers?

## Target
- File/function: `core/src/sigverify.rs` :: `send_votes_to_worker_pool` (around line 96)
- Entrypoint: TPU/TVU packet fetch and sigverify stage — attacker can flood the public entrypoint with unprivileged traffic
- Attacker controls: packet batches, signatures, and dedup/shred inputs
- Exploit idea: Can unprivileged traffic through `send_votes_to_worker_pool` (near line 96) monopolize connection slots/bandwidth/scheduler time and starve honest peers, so that the connection-slot / bandwidth / scheduler share left for honest peers is set to an attacker-chosen or inconsistent value.
- Invariant to test: honest peers keep a fair share of connection/bandwidth/scheduler resources
- Expected Immunefi impact: High. Unprivileged transaction, gossip, or QUIC traffic can starve honest peers of connection slots, stake-weighted bandwidth, scheduler capacity, or thread-pool time, blocking legitimate transactions from ever being included.
- Fast validation: add a focused Rust unit/fuzz test on `send_votes_to_worker_pool` in `core/src/sigverify.rs` measuring honest-request latency under an unprivileged flood.
