# Q2482: node migrations set_backup_service_info a one-time artifact can

## Question
Can an unprivileged NEAR account enter through `sign` and use payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests to drive the code path through `crates/contract/src/node_migrations.rs::set_backup_service_info` so that a one-time artifact can be consumed more than once or after its intended lifetime, breaking the invariant that completed, expired, or superseded state must never be reusable in a later request or epoch, and leading to Bypass of threshold signature requirements?

## Target
- File/function: crates/contract/src/node_migrations.rs:29::set_backup_service_info
- Entrypoint: `sign`
- Attacker controls: payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests
- Exploit idea: a one-time artifact can be consumed more than once or after its intended lifetime
- Invariant to test: completed, expired, or superseded state must never be reusable in a later request or epoch
- Expected Immunefi impact: Bypass of threshold signature requirements
- Fast validation: force a retry or restart boundary, then resend the old artifact and verify whether it still affects request resolution or signature completion
