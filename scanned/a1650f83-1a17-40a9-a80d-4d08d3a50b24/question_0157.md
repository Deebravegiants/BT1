# Q0157: as_multi_threshold_1 can mis-propagate effective origin

## Question
Can an unprivileged attacker reach `as_multi_threshold_1` with crafted nested call payloads, duplicate or adversarial list ordering, batched or wrapped execution context and make authorization check one subject while execution or settlement uses another subject?

## Target
- File/function: substrate/frame/multisig/src/lib.rs::as_multi_threshold_1
- Entrypoint: public dispatch wrapper `as_multi_threshold_1`
- Attacker controls: nested call payloads, duplicate or adversarial list ordering, batched or wrapped execution context
- Exploit idea: Target wrappers where delegated, derived, fallback, or recovered origin is resolved in one place but the economic or governance effect is bound elsewhere.
- Invariant to test: Authorization subject and execution subject must remain identical end-to-end.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Use self-reference, aliasing, proxying, batching, and nested calls to check whether effective origin changes between validation and execution.
