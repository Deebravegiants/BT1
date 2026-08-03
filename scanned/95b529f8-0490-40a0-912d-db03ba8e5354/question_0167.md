# Q0167: poke_deposit can mis-propagate effective origin

## Question
Can an unprivileged attacker reach `poke_deposit` with crafted batched or wrapped execution context and make authorization check one subject while execution or settlement uses another subject?

## Target
- File/function: substrate/frame/proxy/src/lib.rs::poke_deposit
- Entrypoint: public dispatch wrapper `poke_deposit`
- Attacker controls: batched or wrapped execution context
- Exploit idea: Target wrappers where delegated, derived, fallback, or recovered origin is resolved in one place but the economic or governance effect is bound elsewhere.
- Invariant to test: Authorization subject and execution subject must remain identical end-to-end.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Use self-reference, aliasing, proxying, batching, and nested calls to check whether effective origin changes between validation and execution.
