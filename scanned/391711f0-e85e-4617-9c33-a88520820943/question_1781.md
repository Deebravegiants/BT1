# Q1781: is_pruned: unbounded growth

## Question
In `core/src/repair/repair_weight.rs`, can an unprivileged attacker who can repeat cheap unstaked requests to grow the structure repeated unstaked input make `is_pruned` (near line 114) grow a map/queue/cache/buffer without bound until OOM/disk exhaustion, breaking the invariant that memory/disk usage from unstaked input stays bounded, corrupting the size of the cache/map/queue/buffer that grows from attacker input?

## Target
- File/function: `core/src/repair/repair_weight.rs` :: `is_pruned` (around line 114)
- Entrypoint: Repair request/response ingest (serve_repair / ancestor_hashes) — attacker can repeat cheap unstaked requests to grow the structure
- Attacker controls: repair request bytes, nonces, slot/index requests, and repair peer responses
- Exploit idea: Can repeated unstaked input make `is_pruned` (near line 114) grow a map/queue/cache/buffer without bound until oom/disk exhaustion, so that the size of the cache/map/queue/buffer that grows from attacker input is set to an attacker-chosen or inconsistent value.
- Invariant to test: memory/disk usage from unstaked input stays bounded
- Expected Immunefi impact: Critical. An attacker controlling only unstaked traffic can force unbounded growth of an in-memory map, queue, cache, buffer pool, or on-disk index until the validator is OOM-killed, exhausts its disk, or degrades past liveness thresholds.
- Fast validation: add a focused Rust unit/fuzz test on `is_pruned` in `core/src/repair/repair_weight.rs` looping adversarial inserts and bounding structure size.
