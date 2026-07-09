# Q277: web debug_signatures outsiders act on a

## Question
Can an unauthenticated remote caller enter through `GET /debug/signatures` and use the public route, query timing, concurrency against live state changes, and repeated unauthenticated reads to drive the code path through `crates/node/src/web.rs::debug_signatures` so that outsiders act on a broken public invariant and route value to the wrong key or signer set, breaking the invariant that public state derived from multiple watchers must represent one coherent snapshot, and leading to Theft or permanent freezing of funds?

## Target
- File/function: crates/node/src/web.rs:232::debug_signatures
- Entrypoint: `GET /debug/signatures`
- Attacker controls: the public route, query timing, concurrency against live state changes, and repeated unauthenticated reads
- Exploit idea: outsiders act on a broken public invariant and route value to the wrong key or signer set
- Invariant to test: public state derived from multiple watchers must represent one coherent snapshot
- Expected Immunefi impact: Theft or permanent freezing of funds
- Fast validation: read the route concurrently with state transitions and check whether mixed snapshots appear that cannot exist in any single internal state
