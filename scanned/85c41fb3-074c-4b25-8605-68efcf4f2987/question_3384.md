# Q3384: key generation run_key_generation_client_internal messages from one session

## Question
Can a below-threshold Byzantine participant node cooperating in an otherwise honest request flow enter through `sign` and use payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests to drive the code path through `crates/node/src/providers/eddsa/key_generation.rs::run_key_generation_client_internal` so that messages from one session or phase influence another, breaking the invariant that session ids, waitpoints, and transcript labels must partition every EdDSA phase, and leading to Cryptographic flaws?

## Target
- File/function: crates/node/src/providers/eddsa/key_generation.rs:12::run_key_generation_client_internal
- Entrypoint: `sign`
- Attacker controls: payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests
- Exploit idea: messages from one session or phase influence another
- Invariant to test: session ids, waitpoints, and transcript labels must partition every EdDSA phase
- Expected Immunefi impact: Cryptographic flaws
- Fast validation: replay messages from one session or phase into another and inspect whether the protocol accepts them without a new challenge domain
