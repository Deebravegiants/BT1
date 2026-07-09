# Q3382: key generation run_key_generation_client_internal old key-era material remains

## Question
Can a below-threshold Byzantine participant node cooperating in an otherwise honest request flow enter through `sign` and use payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests to drive the code path through `crates/node/src/providers/eddsa/key_generation.rs::run_key_generation_client_internal` so that old key-era material remains live after authority changed, breaking the invariant that nonce, presign, and signing state must be invalidated on key-version or participant-set change, and leading to Unauthorized transaction?

## Target
- File/function: crates/node/src/providers/eddsa/key_generation.rs:12::run_key_generation_client_internal
- Entrypoint: `sign`
- Attacker controls: payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests
- Exploit idea: old key-era material remains live after authority changed
- Invariant to test: nonce, presign, and signing state must be invalidated on key-version or participant-set change
- Expected Immunefi impact: Unauthorized transaction
- Fast validation: capture pre-reshare session material, reshuffle participants or key version, and test whether the old material is still accepted
