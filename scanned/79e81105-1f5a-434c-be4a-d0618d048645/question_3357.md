# Q3357: ecdsa new_channel_for_task honest-looking shares combine under

## Question
Can a below-threshold Byzantine participant node cooperating in an otherwise honest request flow enter through `sign` and use payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests to drive the code path through `crates/node/src/providers/ecdsa.rs::new_channel_for_task` so that honest-looking shares combine under inconsistent math, breaking the invariant that participant ordering and identifier canonicalization must be identical anywhere coefficients, commitments, or transcripts depend on them, and leading to Bypass of threshold signature requirements?

## Target
- File/function: crates/node/src/providers/ecdsa.rs:139::new_channel_for_task
- Entrypoint: `sign`
- Attacker controls: payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests
- Exploit idea: honest-looking shares combine under inconsistent math
- Invariant to test: participant ordering and identifier canonicalization must be identical anywhere coefficients, commitments, or transcripts depend on them
- Expected Immunefi impact: Bypass of threshold signature requirements
- Fast validation: permute the same participant set at different boundaries and compare coefficients, transcripts, and final signature acceptance
