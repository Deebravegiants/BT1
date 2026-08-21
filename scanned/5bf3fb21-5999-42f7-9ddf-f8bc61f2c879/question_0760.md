# Q0760: Retry of a non-idempotent request in save_frame_with_id (agents/image_notary.rs)

## Question
Can an unprivileged attacker induce the retry path in `save_frame_with_id` in [src/agents/image_notary.rs](src/agents/image_notary.rs) for a non-idempotent operation (enrollment submission, custody upload), producing duplicate records or double-attributed biometric data?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `save_frame_with_id` (function)
- Entrypoint: Conditions that induce transient failure and retry
- Attacker controls: timing/size conditions triggering the retry
- Exploit idea: Check `save_frame_with_id` for idempotency keys on retried operations.
- Invariant to test: Every retried operation carries an idempotency key so duplicates are collapsed.
- Expected Immunefi impact: Duplicate or double-attributed biometric enrollment records
- Fast validation: Integration test forcing retries and asserting a stable idempotency key.
