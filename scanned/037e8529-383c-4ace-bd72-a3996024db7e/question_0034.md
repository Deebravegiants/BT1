# Q34: web respond a one-time artifact can

## Question
Can an unauthenticated remote caller enter through `public web route exposed by start_web_server` and use the public route, query timing, concurrency against live state changes, and repeated unauthenticated reads to drive the code path through `crates/node/src/web.rs::respond` so that a one-time artifact can be consumed more than once or after its intended lifetime, breaking the invariant that completed, expired, or superseded state must never be reusable in a later request or epoch, and leading to Bypass of threshold signature requirements?

## Target
- File/function: crates/node/src/web.rs:198::respond
- Entrypoint: `public web route exposed by start_web_server`
- Attacker controls: the public route, query timing, concurrency against live state changes, and repeated unauthenticated reads
- Exploit idea: a one-time artifact can be consumed more than once or after its intended lifetime
- Invariant to test: completed, expired, or superseded state must never be reusable in a later request or epoch
- Expected Immunefi impact: Bypass of threshold signature requirements
- Fast validation: force a retry or restart boundary, then resend the old artifact and verify whether it still affects request resolution or signature completion
