# Q5382: refresh_recent_peers: concurrency/TOCTOU

## Question
In `send-transaction-service/src/tpu_info.rs`, can an unprivileged attacker who can race concurrent requests/transactions on the shared state concurrent unprivileged input create a TOCTOU/lock-ordering/torn-read window at `refresh_recent_peers` (near line 6) yielding stale or freed shared state, breaking the invariant that shared state reads are consistent and free of TOCTOU/torn/stale views, corrupting the shared account/index/cache state observed across concurrent access?

## Target
- File/function: `send-transaction-service/src/tpu_info.rs` :: `refresh_recent_peers` (around line 6)
- Entrypoint: Send-transaction-service retry/forward path — attacker can race concurrent requests/transactions on the shared state
- Attacker controls: submitted transactions, retry queue entries, and forwarding parameters
- Exploit idea: Can concurrent unprivileged input create a toctou/lock-ordering/torn-read window at `refresh_recent_peers` (near line 6) yielding stale or freed shared state, so that the shared account/index/cache state observed across concurrent access is set to an attacker-chosen or inconsistent value.
- Invariant to test: shared state reads are consistent and free of TOCTOU/torn/stale views
- Expected Immunefi impact: High. Time-of-check/time-of-use gaps, unsynchronized shared state, or lock-ordering mistakes on hot validator paths let concurrent unprivileged input produce torn reads, stale account state, deadlock, or use of data freed or replaced mid-operation.
- Fast validation: add a focused Rust unit/fuzz test on `refresh_recent_peers` in `send-transaction-service/src/tpu_info.rs` running loom/concurrent stress and checking for stale/torn state.
