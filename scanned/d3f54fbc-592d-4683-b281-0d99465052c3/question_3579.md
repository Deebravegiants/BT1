# Q3579: recent transactions record one layer authorizes an

## Question
Can an unprivileged NEAR account enter through `sign` and use payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests to drive the code path through `crates/node/src/web/recent_transactions.rs::record` so that one layer authorizes an object another layer would not authorize, breaking the invariant that all codecs and DTO conversions must preserve the same canonical security meaning, and leading to Contract execution flows?

## Target
- File/function: crates/node/src/web/recent_transactions.rs:40::record
- Entrypoint: `sign`
- Attacker controls: payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests
- Exploit idea: one layer authorizes an object another layer would not authorize
- Invariant to test: all codecs and DTO conversions must preserve the same canonical security meaning
- Expected Immunefi impact: Contract execution flows
- Fast validation: round-trip the same attacker-chosen object through every codec used by the public flow and diff hashes, normalized fields, and authorization results
