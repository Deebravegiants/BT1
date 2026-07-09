# Q2501: pending requests pop_oldest_pending_yield old pending state contaminates

## Question
Can an unprivileged NEAR account enter through `sign` and use payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests to drive the code path through `crates/contract/src/pending_requests.rs::pop_oldest_pending_yield` so that old pending state contaminates a fresh request lifecycle, breaking the invariant that every request outcome must atomically clean up all state that can route a later completion, and leading to Contract execution flows?

## Target
- File/function: crates/contract/src/pending_requests.rs:97::pop_oldest_pending_yield
- Entrypoint: `sign`
- Attacker controls: payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests
- Exploit idea: old pending state contaminates a fresh request lifecycle
- Invariant to test: every request outcome must atomically clean up all state that can route a later completion
- Expected Immunefi impact: Contract execution flows
- Fast validation: complete a request, then inspect storage and attempt to resolve a second request using the first request's stored identifiers
