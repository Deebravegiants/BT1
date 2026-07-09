# Q340: web debug_request_from_node unauthenticated debugging surfaces reveal

## Question
Can an unauthenticated remote caller enter through `public web route exposed by start_web_server` and use the public route, query timing, concurrency against live state changes, and repeated unauthenticated reads to drive the code path through `crates/node/src/web.rs::debug_request_from_node` so that unauthenticated debugging surfaces reveal internals that can be reused in a later exploit chain, breaking the invariant that debug-only introspection must not expose security-sensitive state on a default-enabled unauthenticated route, and leading to Information disclosure of sensitive MPC state?

## Target
- File/function: crates/node/src/web.rs:210::debug_request_from_node
- Entrypoint: `public web route exposed by start_web_server`
- Attacker controls: the public route, query timing, concurrency against live state changes, and repeated unauthenticated reads
- Exploit idea: unauthenticated debugging surfaces reveal internals that can be reused in a later exploit chain
- Invariant to test: debug-only introspection must not expose security-sensitive state on a default-enabled unauthenticated route
- Expected Immunefi impact: Information disclosure of sensitive MPC state
- Fast validation: query the route repeatedly during live request processing and compare the response against what an external user should legitimately know
