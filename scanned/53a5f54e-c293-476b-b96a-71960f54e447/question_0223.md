# Q223: sign utils assert_sign_inputs malformed shares slip through

## Question
Can a below-threshold Byzantine participant node cooperating in an otherwise honest request flow enter through `sign` and use payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests to drive the code path through `crates/threshold-signatures/src/frost/sign_utils.rs::assert_sign_inputs` so that malformed shares slip through to aggregation, breaking the invariant that every share and commitment must be canonicalized and curve-checked exactly once before use, and leading to Unauthorized transaction?

## Target
- File/function: crates/threshold-signatures/src/frost/sign_utils.rs:43::assert_sign_inputs
- Entrypoint: `sign`
- Attacker controls: payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests
- Exploit idea: malformed shares slip through to aggregation
- Invariant to test: every share and commitment must be canonicalized and curve-checked exactly once before use
- Expected Immunefi impact: Unauthorized transaction
- Fast validation: fuzz scalar and point encodings at the share boundary and compare parser acceptance with final signature verification
