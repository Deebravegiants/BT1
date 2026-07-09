# Q1893: key state public_key old pending state contaminates

## Question
Can an unprivileged NEAR account enter through `public_key` and use the chosen predecessor override, derivation path, queried domain or curve, and timing relative to key-version changes to drive the code path through `crates/contract/src/primitives/key_state.rs::public_key` so that old pending state contaminates a fresh request lifecycle, breaking the invariant that every request outcome must atomically clean up all state that can route a later completion, and leading to Contract execution flows?

## Target
- File/function: crates/contract/src/primitives/key_state.rs:47::public_key
- Entrypoint: `public_key`
- Attacker controls: the chosen predecessor override, derivation path, queried domain or curve, and timing relative to key-version changes
- Exploit idea: old pending state contaminates a fresh request lifecycle
- Invariant to test: every request outcome must atomically clean up all state that can route a later completion
- Expected Immunefi impact: Contract execution flows
- Fast validation: complete a request, then inspect storage and attempt to resolve a second request using the first request's stored identifiers
