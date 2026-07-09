# Q40: web respond operational configuration that should

## Question
Can an unauthenticated remote caller enter through `public web route exposed by start_web_server` and use the public route, query timing, concurrency against live state changes, and repeated unauthenticated reads to drive the code path through `crates/node/src/web.rs::respond` so that operational configuration that should stay local becomes public exploit guidance, breaking the invariant that public web routes must not disclose authentication, provider-routing, or participant-mapping details beyond what the trust model allows, and leading to Information disclosure of sensitive MPC state?

## Target
- File/function: crates/node/src/web.rs:198::respond
- Entrypoint: `public web route exposed by start_web_server`
- Attacker controls: the public route, query timing, concurrency against live state changes, and repeated unauthenticated reads
- Exploit idea: operational configuration that should stay local becomes public exploit guidance
- Invariant to test: public web routes must not disclose authentication, provider-routing, or participant-mapping details beyond what the trust model allows
- Expected Immunefi impact: Information disclosure of sensitive MPC state
- Fast validation: diff the route response against local configuration sources and mark any field that reduces the search space for a targeted protocol exploit
