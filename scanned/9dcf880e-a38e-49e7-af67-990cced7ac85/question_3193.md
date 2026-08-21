# Q3193: Retry of a non-idempotent request in TieredPackageRequest (backend/presigned_url.rs)

## Question
Can an unprivileged attacker induce the retry path in `TieredPackageRequest` in [src/backend/presigned_url.rs](src/backend/presigned_url.rs) for a non-idempotent operation (enrollment submission, custody upload), producing duplicate records or double-attributed biometric data?

## Target
- File/function: [src/backend/presigned_url.rs](src/backend/presigned_url.rs) -> `TieredPackageRequest` (type)
- Entrypoint: Conditions that induce transient failure and retry
- Attacker controls: timing/size conditions triggering the retry
- Exploit idea: Check `TieredPackageRequest` for idempotency keys on retried operations.
- Invariant to test: Every retried operation carries an idempotency key so duplicates are collapsed.
- Expected Immunefi impact: Duplicate or double-attributed biometric enrollment records
- Fast validation: Integration test forcing retries and asserting a stable idempotency key.
