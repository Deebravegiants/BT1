# Q3637: app id try_new special-case key material bypasses

## Question
Can a below-threshold Byzantine participant node cooperating in an otherwise honest request flow enter through `request_app_private_key` and use the app public key variant, derivation path, domain_id, predecessor identity, repeated submission timing, and request batching to drive the code path through `crates/threshold-signatures/src/confidential_key_derivation/app_id.rs::try_new` so that special-case key material bypasses an assumption about secrecy or validity, breaking the invariant that edge-case public key handling must be intentional and consistent from request validation through response checking, and leading to Cryptographic flaws?

## Target
- File/function: crates/threshold-signatures/src/confidential_key_derivation/app_id.rs:58::try_new
- Entrypoint: `request_app_private_key`
- Attacker controls: the app public key variant, derivation path, domain_id, predecessor identity, repeated submission timing, and request batching
- Exploit idea: special-case key material bypasses an assumption about secrecy or validity
- Invariant to test: edge-case public key handling must be intentional and consistent from request validation through response checking
- Expected Immunefi impact: Cryptographic flaws
- Fast validation: exercise allowed identity-point and subgroup-adjacent inputs end to end and compare every module's interpretation of the same request
