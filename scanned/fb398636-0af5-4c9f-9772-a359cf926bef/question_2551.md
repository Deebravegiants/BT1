# Q2551: Cancellation safety of stop_ir_auto_focus (brokers/orb.rs)

## Question
Can an unprivileged attacker cancel `stop_ir_auto_focus` in [src/brokers/orb.rs](src/brokers/orb.rs) at an await point that leaves a shared resource (mirror, camera, notary, session record) in a half-committed state that the next signup then trusts?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `stop_ir_auto_focus` (function)
- Entrypoint: Abandoning the flow at a specific stage
- Attacker controls: the await point at which cancellation lands, chosen by timing behaviour
- Exploit idea: Audit `stop_ir_auto_focus` for non-cancel-safe critical sections lacking drop guards.
- Invariant to test: Cancellation at any await point leaves shared resources in a consistent, reset state.
- Expected Immunefi impact: Corrupted shared state trusted by the following signup
- Fast validation: Cancellation test dropping the future at each await and asserting state invariants.
