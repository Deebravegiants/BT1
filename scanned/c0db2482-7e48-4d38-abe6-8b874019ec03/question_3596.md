# Q3596: from_data: resource starvation

## Question
In `perf/src/packet.rs`, can an unprivileged attacker who can flood the public entrypoint with unprivileged traffic unprivileged traffic through `from_data` (near line 113) monopolize connection slots/bandwidth/scheduler time and starve honest peers, breaking the invariant that honest peers keep a fair share of connection/bandwidth/scheduler resources, corrupting the connection-slot / bandwidth / scheduler share left for honest peers?

## Target
- File/function: `perf/src/packet.rs` :: `from_data` (around line 113)
- Entrypoint: QUIC/TPU packet ingest and connection handling — attacker can flood the public entrypoint with unprivileged traffic
- Attacker controls: QUIC streams, packet batches, connection counts, and stake-weighting inputs
- Exploit idea: Can unprivileged traffic through `from_data` (near line 113) monopolize connection slots/bandwidth/scheduler time and starve honest peers, so that the connection-slot / bandwidth / scheduler share left for honest peers is set to an attacker-chosen or inconsistent value.
- Invariant to test: honest peers keep a fair share of connection/bandwidth/scheduler resources
- Expected Immunefi impact: High. Unprivileged transaction, gossip, or QUIC traffic can starve honest peers of connection slots, stake-weighted bandwidth, scheduler capacity, or thread-pool time, blocking legitimate transactions from ever being included.
- Fast validation: add a focused Rust unit/fuzz test on `from_data` in `perf/src/packet.rs` measuring honest-request latency under an unprivileged flood.
