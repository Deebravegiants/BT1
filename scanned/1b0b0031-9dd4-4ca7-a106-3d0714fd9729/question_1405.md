# Q1405: Cancellation safety of init_data_uploader (brokers/orb.rs)

## Question
Can an unprivileged attacker cancel `init_data_uploader` in [src/brokers/orb.rs](src/brokers/orb.rs) at an await point that leaves a shared resource (mirror, camera, notary, session record) in a half-committed state that the next signup then trusts?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `init_data_uploader` (function)
- Entrypoint: Abandoning the flow at a specific stage
- Attacker controls: the await point at which cancellation lands, chosen by timing behaviour
- Exploit idea: Audit `init_data_uploader` for non-cancel-safe critical sections lacking drop guards.
- Invariant to test: Cancellation at any await point leaves shared resources in a consistent, reset state.
- Expected Immunefi impact: Corrupted shared state trusted by the following signup
- Fast validation: Cancellation test dropping the future at each await and asserting state invariants.
