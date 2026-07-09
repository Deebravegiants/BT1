# Q618: state start_keygen_instance a one-time artifact can

## Question
Can an unprivileged NEAR account enter through `sign` and use payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests to drive the code path through `crates/contract/src/state.rs::start_keygen_instance` so that a one-time artifact can be consumed more than once or after its intended lifetime, breaking the invariant that completed, expired, or superseded state must never be reusable in a later request or epoch, and leading to Bypass of threshold signature requirements?

## Target
- File/function: crates/contract/src/state.rs:67::start_keygen_instance
- Entrypoint: `sign`
- Attacker controls: payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests
- Exploit idea: a one-time artifact can be consumed more than once or after its intended lifetime
- Invariant to test: completed, expired, or superseded state must never be reusable in a later request or epoch
- Expected Immunefi impact: Bypass of threshold signature requirements
- Fast validation: force a retry or restart boundary, then resend the old artifact and verify whether it still affects request resolution or signature completion
