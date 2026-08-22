# Q4478: write_transaction_status_batch: concurrency/TOCTOU

## Question
In `rpc/src/transaction_status_service.rs`, can an unprivileged attacker who can race concurrent requests/transactions on the shared state concurrent unprivileged input create a TOCTOU/lock-ordering/torn-read window at `write_transaction_status_batch` (near line 25) yielding stale or freed shared state, breaking the invariant that shared state reads are consistent and free of TOCTOU/torn/stale views, corrupting the shared account/index/cache state observed across concurrent access?

## Target
- File/function: `rpc/src/transaction_status_service.rs` :: `write_transaction_status_batch` (around line 25)
- Entrypoint: Built-in JSON-RPC / PubSub request handler — attacker can race concurrent requests/transactions on the shared state
- Attacker controls: RPC request params, filters, subscription requests, and pagination inputs
- Exploit idea: Can concurrent unprivileged input create a toctou/lock-ordering/torn-read window at `write_transaction_status_batch` (near line 25) yielding stale or freed shared state, so that the shared account/index/cache state observed across concurrent access is set to an attacker-chosen or inconsistent value.
- Invariant to test: shared state reads are consistent and free of TOCTOU/torn/stale views
- Expected Immunefi impact: High. Time-of-check/time-of-use gaps, unsynchronized shared state, or lock-ordering mistakes on hot validator paths let concurrent unprivileged input produce torn reads, stale account state, deadlock, or use of data freed or replaced mid-operation.
- Fast validation: add a focused Rust unit/fuzz test on `write_transaction_status_batch` in `rpc/src/transaction_status_service.rs` running loom/concurrent stress and checking for stale/torn state.
