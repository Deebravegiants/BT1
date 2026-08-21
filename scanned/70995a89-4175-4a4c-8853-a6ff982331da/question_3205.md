# Q3205: Retry of a non-idempotent request in propagate_to_ui (config.rs)

## Question
Can an unprivileged attacker induce the retry path in `propagate_to_ui` in [src/config.rs](src/config.rs) for a non-idempotent operation (enrollment submission, custody upload), producing duplicate records or double-attributed biometric data?

## Target
- File/function: [src/config.rs](src/config.rs) -> `propagate_to_ui` (function)
- Entrypoint: Conditions that induce transient failure and retry
- Attacker controls: timing/size conditions triggering the retry
- Exploit idea: Check `propagate_to_ui` for idempotency keys on retried operations.
- Invariant to test: Every retried operation carries an idempotency key so duplicates are collapsed.
- Expected Immunefi impact: Duplicate or double-attributed biometric enrollment records
- Fast validation: Integration test forcing retries and asserting a stable idempotency key.
