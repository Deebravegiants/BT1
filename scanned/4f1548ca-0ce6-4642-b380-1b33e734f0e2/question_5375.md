# Q5375: get_max_retries: concurrency/TOCTOU

## Question
In `send-transaction-service/src/send_transaction_service.rs`, can an unprivileged attacker who can race concurrent requests/transactions on the shared state concurrent unprivileged input create a TOCTOU/lock-ordering/torn-read window at `get_max_retries` (near line 161) yielding stale or freed shared state, breaking the invariant that shared state reads are consistent and free of TOCTOU/torn/stale views, corrupting the shared account/index/cache state observed across concurrent access?

## Target
- File/function: `send-transaction-service/src/send_transaction_service.rs` :: `get_max_retries` (around line 161)
- Entrypoint: Send-transaction-service retry/forward path — attacker can race concurrent requests/transactions on the shared state
- Attacker controls: submitted transactions, retry queue entries, and forwarding parameters
- Exploit idea: Can concurrent unprivileged input create a toctou/lock-ordering/torn-read window at `get_max_retries` (near line 161) yielding stale or freed shared state, so that the shared account/index/cache state observed across concurrent access is set to an attacker-chosen or inconsistent value.
- Invariant to test: shared state reads are consistent and free of TOCTOU/torn/stale views
- Expected Immunefi impact: High. Time-of-check/time-of-use gaps, unsynchronized shared state, or lock-ordering mistakes on hot validator paths let concurrent unprivileged input produce torn reads, stale account state, deadlock, or use of data freed or replaced mid-operation.
- Fast validation: add a focused Rust unit/fuzz test on `get_max_retries` in `send-transaction-service/src/send_transaction_service.rs` running loom/concurrent stress and checking for stale/torn state.
