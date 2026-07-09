# Q279: web debug_signatures information disclosure becomes an

## Question
Can an unauthenticated remote caller enter through `GET /debug/signatures` and use the public route, query timing, concurrency against live state changes, and repeated unauthenticated reads to drive the code path through `crates/node/src/web.rs::debug_signatures` so that information disclosure becomes an exploit multiplier for another in-scope bug class, breaking the invariant that public diagnostics must not expose reusable request identifiers, pending-state keys, or exact timing windows, and leading to Information disclosure of sensitive MPC state?

## Target
- File/function: crates/node/src/web.rs:232::debug_signatures
- Entrypoint: `GET /debug/signatures`
- Attacker controls: the public route, query timing, concurrency against live state changes, and repeated unauthenticated reads
- Exploit idea: information disclosure becomes an exploit multiplier for another in-scope bug class
- Invariant to test: public diagnostics must not expose reusable request identifiers, pending-state keys, or exact timing windows
- Expected Immunefi impact: Information disclosure of sensitive MPC state
- Fast validation: observe whether the route leaks identifiers or timestamps that can be fed back into a second exploit attempt against request resolution or transport state
