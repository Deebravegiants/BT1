# Q2068: new_with_client: unbounded growth

## Question
In `core/src/tpu.rs`, can an unprivileged attacker who can repeat cheap unstaked requests to grow the structure repeated unstaked input make `new_with_client` (near line 118) grow a map/queue/cache/buffer without bound until OOM/disk exhaustion, breaking the invariant that memory/disk usage from unstaked input stays bounded, corrupting the size of the cache/map/queue/buffer that grows from attacker input?

## Target
- File/function: `core/src/tpu.rs` :: `new_with_client` (around line 118)
- Entrypoint: TPU/TVU packet fetch and sigverify stage — attacker can repeat cheap unstaked requests to grow the structure
- Attacker controls: packet batches, signatures, and dedup/shred inputs
- Exploit idea: Can repeated unstaked input make `new_with_client` (near line 118) grow a map/queue/cache/buffer without bound until oom/disk exhaustion, so that the size of the cache/map/queue/buffer that grows from attacker input is set to an attacker-chosen or inconsistent value.
- Invariant to test: memory/disk usage from unstaked input stays bounded
- Expected Immunefi impact: Critical. An attacker controlling only unstaked traffic can force unbounded growth of an in-memory map, queue, cache, buffer pool, or on-disk index until the validator is OOM-killed, exhausts its disk, or degrades past liveness thresholds.
- Fast validation: add a focused Rust unit/fuzz test on `new_with_client` in `core/src/tpu.rs` looping adversarial inserts and bounding structure size.
