# Q2749: state params_to_string invalid or more-privileged semantics

## Question
Can an unprivileged NEAR account enter through `sign` and use payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests to drive the code path through `crates/near-mpc-contract-interface/src/types/state.rs::params_to_string` so that invalid or more-privileged semantics are reached through a decoding ambiguity, breaking the invariant that every externally reachable variant and default path must be explicit and equally validated, and leading to Unauthorized access to MPC key shares or signing capability?

## Target
- File/function: crates/near-mpc-contract-interface/src/types/state.rs:282::params_to_string
- Entrypoint: `sign`
- Attacker controls: payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests
- Exploit idea: invalid or more-privileged semantics are reached through a decoding ambiguity
- Invariant to test: every externally reachable variant and default path must be explicit and equally validated
- Expected Immunefi impact: Unauthorized access to MPC key shares or signing capability
- Fast validation: fuzz missing fields, alternate variant spellings, and defaultable values, then diff the runtime object against the caller's intended object
