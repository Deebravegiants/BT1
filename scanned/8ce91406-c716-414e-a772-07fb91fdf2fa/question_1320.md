# Q1320: debug add_completed_request old stored bytes silently

## Question
Can an unprivileged NEAR account enter through `sign` and use payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests to drive the code path through `crates/node/src/requests/debug.rs::add_completed_request` so that old stored bytes silently change meaning in security-sensitive state, breaking the invariant that durable serialized state must remain backward-compatible without changing the authorization meaning of existing bytes, and leading to Contract execution flows?

## Target
- File/function: crates/node/src/requests/debug.rs:78::add_completed_request
- Entrypoint: `sign`
- Attacker controls: payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests
- Exploit idea: old stored bytes silently change meaning in security-sensitive state
- Invariant to test: durable serialized state must remain backward-compatible without changing the authorization meaning of existing bytes
- Expected Immunefi impact: Contract execution flows
- Fast validation: persist crafted state bytes through one representation, reload through the next conversion path, and diff the resulting runtime security state
