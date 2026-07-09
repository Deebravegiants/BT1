# Q3604: recent transactions spawn_recent_transactions_drain distinct objects share the

## Question
Can an unprivileged NEAR account enter through `sign` and use payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests to drive the code path through `crates/node/src/web/recent_transactions.rs::spawn_recent_transactions_drain` so that distinct objects share the same identity or one object has multiple effective identities, breaking the invariant that security identities must be computed from one canonical serialized form, and leading to Unauthorized transaction?

## Target
- File/function: crates/node/src/web/recent_transactions.rs:116::spawn_recent_transactions_drain
- Entrypoint: `sign`
- Attacker controls: payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests
- Exploit idea: distinct objects share the same identity or one object has multiple effective identities
- Invariant to test: security identities must be computed from one canonical serialized form
- Expected Immunefi impact: Unauthorized transaction
- Fast validation: construct semantically equivalent encodings that differ only in ordering, padding, or representation and compare derived hashes and storage lookups
