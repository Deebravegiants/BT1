# Q367: web start_web_server information disclosure becomes an

## Question
Can an unauthenticated remote caller enter through `public web route exposed by start_web_server` and use the public route, query timing, concurrency against live state changes, and repeated unauthenticated reads to drive the code path through `crates/node/src/web.rs::start_web_server` so that information disclosure becomes an exploit multiplier for another in-scope bug class, breaking the invariant that public diagnostics must not expose reusable request identifiers, pending-state keys, or exact timing windows, and leading to Information disclosure of sensitive MPC state?

## Target
- File/function: crates/node/src/web.rs:322::start_web_server
- Entrypoint: `public web route exposed by start_web_server`
- Attacker controls: the public route, query timing, concurrency against live state changes, and repeated unauthenticated reads
- Exploit idea: information disclosure becomes an exploit multiplier for another in-scope bug class
- Invariant to test: public diagnostics must not expose reusable request identifiers, pending-state keys, or exact timing windows
- Expected Immunefi impact: Information disclosure of sensitive MPC state
- Fast validation: observe whether the route leaks identifiers or timestamps that can be fed back into a second exploit attempt against request resolution or transport state
