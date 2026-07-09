# Q3663: scalar wrapper zeroize one request can consume

## Question
Can a below-threshold Byzantine participant node cooperating in an otherwise honest request flow enter through `request_app_private_key` and use the app public key variant, derivation path, domain_id, predecessor identity, repeated submission timing, and request batching to drive the code path through `crates/threshold-signatures/src/confidential_key_derivation/scalar_wrapper.rs::zeroize` so that one request can consume or influence another request's derivation material, breaking the invariant that CKD session state must be isolated per request and per application identity, and leading to Unauthorized access to MPC key shares or signing capability?

## Target
- File/function: crates/threshold-signatures/src/confidential_key_derivation/scalar_wrapper.rs:27::zeroize
- Entrypoint: `request_app_private_key`
- Attacker controls: the app public key variant, derivation path, domain_id, predecessor identity, repeated submission timing, and request batching
- Exploit idea: one request can consume or influence another request's derivation material
- Invariant to test: CKD session state must be isolated per request and per application identity
- Expected Immunefi impact: Unauthorized access to MPC key shares or signing capability
- Fast validation: run concurrent CKD requests with nearly identical inputs and trace whether intermediate identifiers or outputs cross between sessions
