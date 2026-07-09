# Q365: web start_web_server outsiders act on a

## Question
Can an unauthenticated remote caller enter through `public web route exposed by start_web_server` and use the public route, query timing, concurrency against live state changes, and repeated unauthenticated reads to drive the code path through `crates/node/src/web.rs::start_web_server` so that outsiders act on a broken public invariant and route value to the wrong key or signer set, breaking the invariant that public state derived from multiple watchers must represent one coherent snapshot, and leading to Theft or permanent freezing of funds?

## Target
- File/function: crates/node/src/web.rs:322::start_web_server
- Entrypoint: `public web route exposed by start_web_server`
- Attacker controls: the public route, query timing, concurrency against live state changes, and repeated unauthenticated reads
- Exploit idea: outsiders act on a broken public invariant and route value to the wrong key or signer set
- Invariant to test: public state derived from multiple watchers must represent one coherent snapshot
- Expected Immunefi impact: Theft or permanent freezing of funds
- Fast validation: read the route concurrently with state transitions and check whether mixed snapshots appear that cannot exist in any single internal state
