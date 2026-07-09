# Q5: lib respond_verify_foreign_tx old pending state contaminates

## Question
Can a below-threshold Byzantine participant node acting through an attested responder account enter through `respond_verify_foreign_tx` and use the authenticated responder's submitted response object, request body, submission timing, stale local session state, and any replayable MPC artifacts visible before response submission to drive the code path through `crates/contract/src/lib.rs::respond_verify_foreign_tx` so that old pending state contaminates a fresh request lifecycle, breaking the invariant that every request outcome must atomically clean up all state that can route a later completion, and leading to Contract execution flows?

## Target
- File/function: crates/contract/src/lib.rs:692::respond_verify_foreign_tx
- Entrypoint: `respond_verify_foreign_tx`
- Attacker controls: the authenticated responder's submitted response object, request body, submission timing, stale local session state, and any replayable MPC artifacts visible before response submission
- Exploit idea: old pending state contaminates a fresh request lifecycle
- Invariant to test: every request outcome must atomically clean up all state that can route a later completion
- Expected Immunefi impact: Contract execution flows
- Fast validation: complete a request, then inspect storage and attempt to resolve a second request using the first request's stored identifiers
