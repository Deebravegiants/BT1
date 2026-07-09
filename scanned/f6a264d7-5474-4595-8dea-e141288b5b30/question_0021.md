# Q21: lib verify_foreign_transaction old pending state contaminates

## Question
Can an unprivileged NEAR account enter through `verify_foreign_transaction` and use the chosen chain/domain, transaction identifier, proof bytes, event/log shape, repeated submissions, and replay timing to drive the code path through `crates/contract/src/lib.rs::verify_foreign_transaction` so that old pending state contaminates a fresh request lifecycle, breaking the invariant that every request outcome must atomically clean up all state that can route a later completion, and leading to Contract execution flows?

## Target
- File/function: crates/contract/src/lib.rs:519::verify_foreign_transaction
- Entrypoint: `verify_foreign_transaction`
- Attacker controls: the chosen chain/domain, transaction identifier, proof bytes, event/log shape, repeated submissions, and replay timing
- Exploit idea: old pending state contaminates a fresh request lifecycle
- Invariant to test: every request outcome must atomically clean up all state that can route a later completion
- Expected Immunefi impact: Contract execution flows
- Fast validation: complete a request, then inspect storage and attempt to resolve a second request using the first request's stored identifiers
