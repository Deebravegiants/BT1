# Q1890: key state public_key a one-time artifact can

## Question
Can an unprivileged NEAR account enter through `public_key` and use the chosen predecessor override, derivation path, queried domain or curve, and timing relative to key-version changes to drive the code path through `crates/contract/src/primitives/key_state.rs::public_key` so that a one-time artifact can be consumed more than once or after its intended lifetime, breaking the invariant that completed, expired, or superseded state must never be reusable in a later request or epoch, and leading to Bypass of threshold signature requirements?

## Target
- File/function: crates/contract/src/primitives/key_state.rs:47::public_key
- Entrypoint: `public_key`
- Attacker controls: the chosen predecessor override, derivation path, queried domain or curve, and timing relative to key-version changes
- Exploit idea: a one-time artifact can be consumed more than once or after its intended lifetime
- Invariant to test: completed, expired, or superseded state must never be reusable in a later request or epoch
- Expected Immunefi impact: Bypass of threshold signature requirements
- Fast validation: force a retry or restart boundary, then resend the old artifact and verify whether it still affects request resolution or signature completion
