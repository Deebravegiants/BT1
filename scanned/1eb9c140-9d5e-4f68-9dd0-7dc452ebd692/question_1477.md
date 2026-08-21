# Q1477: UI/consent state desynchronized from event_loop (ui/mod.rs)

## Question
Can an unprivileged attacker make the state signalled to the user by the UI diverge from the state actually used by `event_loop` in [src/ui/mod.rs](src/ui/mod.rs), so the person being captured consents to one thing while a different policy/identity is recorded?

## Target
- File/function: [src/ui/mod.rs](src/ui/mod.rs) -> `event_loop` (function)
- Entrypoint: Manipulating stage timing so the UI lags the internal state
- Attacker controls: the timing of presence/absence around the consent signal
- Exploit idea: Compare the value driving the UI with the value used in `event_loop` at the same instant.
- Invariant to test: Displayed consent state and enforced consent state are derived from one source of truth.
- Expected Immunefi impact: Biometric capture recorded under a policy the user did not consent to
- Fast validation: Integration test asserting UI signal and enforced policy are always the same value.
