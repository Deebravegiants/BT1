# Q2781: background num_in_flight_atomic invalid or more-privileged semantics

## Question
Can an unprivileged NEAR account enter through `sign` and use payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests to drive the code path through `crates/node/src/background.rs::num_in_flight_atomic` so that invalid or more-privileged semantics are reached through a decoding ambiguity, breaking the invariant that every externally reachable variant and default path must be explicit and equally validated, and leading to Unauthorized access to MPC key shares or signing capability?

## Target
- File/function: crates/node/src/background.rs:24::num_in_flight_atomic
- Entrypoint: `sign`
- Attacker controls: payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests
- Exploit idea: invalid or more-privileged semantics are reached through a decoding ambiguity
- Invariant to test: every externally reachable variant and default path must be explicit and equally validated
- Expected Immunefi impact: Unauthorized access to MPC key shares or signing capability
- Fast validation: fuzz missing fields, alternate variant spellings, and defaultable values, then diff the runtime object against the caller's intended object
