# Q1873: Retry of a non-idempotent request in make_hashes_json (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker induce the retry path in `make_hashes_json` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) for a non-idempotent operation (enrollment submission, custody upload), producing duplicate records or double-attributed biometric data?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `make_hashes_json` (function)
- Entrypoint: Conditions that induce transient failure and retry
- Attacker controls: timing/size conditions triggering the retry
- Exploit idea: Check `make_hashes_json` for idempotency keys on retried operations.
- Invariant to test: Every retried operation carries an idempotency key so duplicates are collapsed.
- Expected Immunefi impact: Duplicate or double-attributed biometric enrollment records
- Fast validation: Integration test forcing retries and asserting a stable idempotency key.
