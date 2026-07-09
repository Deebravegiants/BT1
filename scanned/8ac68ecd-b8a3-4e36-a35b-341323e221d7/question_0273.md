# Q273: web debug_signatures cross-request aliasing lets one

## Question
Can an unauthenticated remote caller enter through `GET /debug/signatures` and use the public route, query timing, concurrency against live state changes, and repeated unauthenticated reads to drive the code path through `crates/node/src/web.rs::debug_signatures` so that cross-request aliasing lets one operation resolve, overwrite, or consume another, breaking the invariant that one externally created operation must map to exactly one internal request record and exactly one completion path, and leading to Unauthorized transaction?

## Target
- File/function: crates/node/src/web.rs:232::debug_signatures
- Entrypoint: `GET /debug/signatures`
- Attacker controls: the public route, query timing, concurrency against live state changes, and repeated unauthenticated reads
- Exploit idea: cross-request aliasing lets one operation resolve, overwrite, or consume another
- Invariant to test: one externally created operation must map to exactly one internal request record and exactly one completion path
- Expected Immunefi impact: Unauthorized transaction
- Fast validation: build two requests that differ in security-relevant fields, trace the hash/key path, and check whether one completion resolves both records or the wrong record
