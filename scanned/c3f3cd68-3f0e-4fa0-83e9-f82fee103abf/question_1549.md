# Q1549: pending requests resolve_yields_for old pending state contaminates

## Question
Can an unprivileged NEAR account enter through `sign` and use payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests to drive the code path through `crates/contract/src/pending_requests.rs::resolve_yields_for` so that old pending state contaminates a fresh request lifecycle, breaking the invariant that every request outcome must atomically clean up all state that can route a later completion, and leading to Contract execution flows?

## Target
- File/function: crates/contract/src/pending_requests.rs:66::resolve_yields_for
- Entrypoint: `sign`
- Attacker controls: payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests
- Exploit idea: old pending state contaminates a fresh request lifecycle
- Invariant to test: every request outcome must atomically clean up all state that can route a later completion
- Expected Immunefi impact: Contract execution flows
- Fast validation: complete a request, then inspect storage and attempt to resolve a second request using the first request's stored identifiers
