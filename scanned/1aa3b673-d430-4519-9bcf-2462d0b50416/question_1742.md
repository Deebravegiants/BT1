# Q1742: batch random ot batch_random_ot_sender_many invalid shares survive parsing

## Question
Can a below-threshold Byzantine participant node cooperating in an otherwise honest request flow enter through `sign` and use payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests to drive the code path through `crates/threshold-signatures/src/ecdsa/ot_based_ecdsa/triples/batch_random_ot.rs::batch_random_ot_sender_many` so that invalid shares survive parsing and influence aggregation, breaking the invariant that share parsing, scalar reduction, and curve-point validation must reject every non-canonical representation before aggregation, and leading to Unauthorized transaction?

## Target
- File/function: crates/threshold-signatures/src/ecdsa/ot_based_ecdsa/triples/batch_random_ot.rs:115::batch_random_ot_sender_many
- Entrypoint: `sign`
- Attacker controls: payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests
- Exploit idea: invalid shares survive parsing and influence aggregation
- Invariant to test: share parsing, scalar reduction, and curve-point validation must reject every non-canonical representation before aggregation
- Expected Immunefi impact: Unauthorized transaction
- Fast validation: fuzz edge-case scalar and point encodings and compare parser acceptance with downstream aggregation and signature verification behavior
