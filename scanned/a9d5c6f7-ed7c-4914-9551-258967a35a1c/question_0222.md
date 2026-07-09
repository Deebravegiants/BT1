# Q222: sign utils assert_sign_inputs old key-era material remains

## Question
Can a below-threshold Byzantine participant node cooperating in an otherwise honest request flow enter through `sign` and use payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests to drive the code path through `crates/threshold-signatures/src/frost/sign_utils.rs::assert_sign_inputs` so that old key-era material remains live after authority changed, breaking the invariant that nonce, presign, and signing state must be invalidated on key-version or participant-set change, and leading to Unauthorized transaction?

## Target
- File/function: crates/threshold-signatures/src/frost/sign_utils.rs:43::assert_sign_inputs
- Entrypoint: `sign`
- Attacker controls: payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests
- Exploit idea: old key-era material remains live after authority changed
- Invariant to test: nonce, presign, and signing state must be invalidated on key-version or participant-set change
- Expected Immunefi impact: Unauthorized transaction
- Fast validation: capture pre-reshare session material, reshuffle participants or key version, and test whether the old material is still accepted
