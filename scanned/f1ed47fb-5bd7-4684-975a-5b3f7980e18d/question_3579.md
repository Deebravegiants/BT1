# Q3579: Cancellation safety of qr_scan_timeout (plans/mod.rs)

## Question
Can an unprivileged attacker cancel `qr_scan_timeout` in [src/plans/mod.rs](src/plans/mod.rs) at an await point that leaves a shared resource (mirror, camera, notary, session record) in a half-committed state that the next signup then trusts?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `qr_scan_timeout` (function)
- Entrypoint: Abandoning the flow at a specific stage
- Attacker controls: the await point at which cancellation lands, chosen by timing behaviour
- Exploit idea: Audit `qr_scan_timeout` for non-cancel-safe critical sections lacking drop guards.
- Invariant to test: Cancellation at any await point leaves shared resources in a consistent, reset state.
- Expected Immunefi impact: Corrupted shared state trusted by the following signup
- Fast validation: Cancellation test dropping the future at each await and asserting state invariants.
