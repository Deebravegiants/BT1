# Q38: web respond users or integrators trust

## Question
Can an unauthenticated remote caller enter through `public web route exposed by start_web_server` and use the public route, query timing, concurrency against live state changes, and repeated unauthenticated reads to drive the code path through `crates/node/src/web.rs::respond` so that users or integrators trust a public representation that is not the real authority source, breaking the invariant that publicly exposed key, attestation, and config views must faithfully encode the effective runtime state, and leading to Unauthorized transaction?

## Target
- File/function: crates/node/src/web.rs:198::respond
- Entrypoint: `public web route exposed by start_web_server`
- Attacker controls: the public route, query timing, concurrency against live state changes, and repeated unauthenticated reads
- Exploit idea: users or integrators trust a public representation that is not the real authority source
- Invariant to test: publicly exposed key, attestation, and config views must faithfully encode the effective runtime state
- Expected Immunefi impact: Unauthorized transaction
- Fast validation: compare the route response against the internal objects immediately before and after a request that depends on the same fields
