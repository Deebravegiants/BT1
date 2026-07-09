# Q280: web debug_signatures operational configuration that should

## Question
Can an unauthenticated remote caller enter through `GET /debug/signatures` and use the public route, query timing, concurrency against live state changes, and repeated unauthenticated reads to drive the code path through `crates/node/src/web.rs::debug_signatures` so that operational configuration that should stay local becomes public exploit guidance, breaking the invariant that public web routes must not disclose authentication, provider-routing, or participant-mapping details beyond what the trust model allows, and leading to Information disclosure of sensitive MPC state?

## Target
- File/function: crates/node/src/web.rs:232::debug_signatures
- Entrypoint: `GET /debug/signatures`
- Attacker controls: the public route, query timing, concurrency against live state changes, and repeated unauthenticated reads
- Exploit idea: operational configuration that should stay local becomes public exploit guidance
- Invariant to test: public web routes must not disclose authentication, provider-routing, or participant-mapping details beyond what the trust model allows
- Expected Immunefi impact: Information disclosure of sensitive MPC state
- Fast validation: diff the route response against local configuration sources and mark any field that reduces the search space for a targeted protocol exploit
