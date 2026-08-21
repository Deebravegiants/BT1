# Q3146: Retry of a non-idempotent request in MANAGEMENT_BACKEND_URL (backend/endpoints.rs)

## Question
Can an unprivileged attacker induce the retry path in `MANAGEMENT_BACKEND_URL` in [src/backend/endpoints.rs](src/backend/endpoints.rs) for a non-idempotent operation (enrollment submission, custody upload), producing duplicate records or double-attributed biometric data?

## Target
- File/function: [src/backend/endpoints.rs](src/backend/endpoints.rs) -> `MANAGEMENT_BACKEND_URL` (item)
- Entrypoint: Conditions that induce transient failure and retry
- Attacker controls: timing/size conditions triggering the retry
- Exploit idea: Check `MANAGEMENT_BACKEND_URL` for idempotency keys on retried operations.
- Invariant to test: Every retried operation carries an idempotency key so duplicates are collapsed.
- Expected Immunefi impact: Duplicate or double-attributed biometric enrollment records
- Fast validation: Integration test forcing retries and asserting a stable idempotency key.
