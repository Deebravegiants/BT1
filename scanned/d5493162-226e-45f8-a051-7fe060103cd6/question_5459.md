# Q5459: ban: unbounded growth

## Question
In `streamer/src/nonblocking/simple_qos.rs`, can an unprivileged attacker who can repeat cheap unstaked requests to grow the structure repeated unstaked input make `ban` (near line 513) grow a map/queue/cache/buffer without bound until OOM/disk exhaustion, breaking the invariant that memory/disk usage from unstaked input stays bounded, corrupting the size of the cache/map/queue/buffer that grows from attacker input?

## Target
- File/function: `streamer/src/nonblocking/simple_qos.rs` :: `ban` (around line 513)
- Entrypoint: QUIC/TPU packet ingest and connection handling — attacker can repeat cheap unstaked requests to grow the structure
- Attacker controls: QUIC streams, packet batches, connection counts, and stake-weighting inputs
- Exploit idea: Can repeated unstaked input make `ban` (near line 513) grow a map/queue/cache/buffer without bound until oom/disk exhaustion, so that the size of the cache/map/queue/buffer that grows from attacker input is set to an attacker-chosen or inconsistent value.
- Invariant to test: memory/disk usage from unstaked input stays bounded
- Expected Immunefi impact: Critical. An attacker controlling only unstaked traffic can force unbounded growth of an in-memory map, queue, cache, buffer pool, or on-disk index until the validator is OOM-killed, exhausts its disk, or degrades past liveness thresholds.
- Fast validation: add a focused Rust unit/fuzz test on `ban` in `streamer/src/nonblocking/simple_qos.rs` looping adversarial inserts and bounding structure size.
