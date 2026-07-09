# Q35: web respond public telemetry becomes sensitive

## Question
Can an unauthenticated remote caller enter through `public web route exposed by start_web_server` and use the public route, query timing, concurrency against live state changes, and repeated unauthenticated reads to drive the code path through `crates/node/src/web.rs::respond` so that public telemetry becomes sensitive MPC-state disclosure, breaking the invariant that outsiders should learn only what is necessary for health checks and public protocol use, and leading to Information disclosure of sensitive MPC state?

## Target
- File/function: crates/node/src/web.rs:198::respond
- Entrypoint: `public web route exposed by start_web_server`
- Attacker controls: the public route, query timing, concurrency against live state changes, and repeated unauthenticated reads
- Exploit idea: public telemetry becomes sensitive MPC-state disclosure
- Invariant to test: outsiders should learn only what is necessary for health checks and public protocol use
- Expected Immunefi impact: Information disclosure of sensitive MPC state
- Fast validation: inventory the exact response fields, correlate them with live request or participant behavior, and verify whether they reveal reusable security state
