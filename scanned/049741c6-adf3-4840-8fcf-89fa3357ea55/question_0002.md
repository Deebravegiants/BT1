# Q2: lib respond_verify_foreign_tx a one-time artifact can

## Question
Can a below-threshold Byzantine participant node acting through an attested responder account enter through `respond_verify_foreign_tx` and use the authenticated responder's submitted response object, request body, submission timing, stale local session state, and any replayable MPC artifacts visible before response submission to drive the code path through `crates/contract/src/lib.rs::respond_verify_foreign_tx` so that a one-time artifact can be consumed more than once or after its intended lifetime, breaking the invariant that completed, expired, or superseded state must never be reusable in a later request or epoch, and leading to Bypass of threshold signature requirements?

## Target
- File/function: crates/contract/src/lib.rs:692::respond_verify_foreign_tx
- Entrypoint: `respond_verify_foreign_tx`
- Attacker controls: the authenticated responder's submitted response object, request body, submission timing, stale local session state, and any replayable MPC artifacts visible before response submission
- Exploit idea: a one-time artifact can be consumed more than once or after its intended lifetime
- Invariant to test: completed, expired, or superseded state must never be reusable in a later request or epoch
- Expected Immunefi impact: Bypass of threshold signature requirements
- Fast validation: force a retry or restart boundary, then resend the old artifact and verify whether it still affects request resolution or signature completion
