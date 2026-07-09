# Q109: presign do_presign valid-looking shares combine under

## Question
Can a below-threshold Byzantine participant node cooperating in an otherwise honest request flow enter through `sign` and use payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests to drive the code path through `crates/threshold-signatures/src/frost/presign.rs::do_presign` so that valid-looking shares combine under inconsistent participant identities, breaking the invariant that all participant-dependent EdDSA computations must use the same canonical participant ordering, and leading to Bypass of threshold signature requirements?

## Target
- File/function: crates/threshold-signatures/src/frost/presign.rs:71::do_presign
- Entrypoint: `sign`
- Attacker controls: payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests
- Exploit idea: valid-looking shares combine under inconsistent participant identities
- Invariant to test: all participant-dependent EdDSA computations must use the same canonical participant ordering
- Expected Immunefi impact: Bypass of threshold signature requirements
- Fast validation: reorder the same participant set at different entry boundaries and compare key package, transcript, and signature-share acceptance
