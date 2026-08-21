# Q0091: UI/consent state desynchronized from handle_user_qr_code (plans/mod.rs)

## Question
Can an unprivileged attacker make the state signalled to the user by the UI diverge from the state actually used by `handle_user_qr_code` in [src/plans/mod.rs](src/plans/mod.rs), so the person being captured consents to one thing while a different policy/identity is recorded?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `handle_user_qr_code` (function)
- Entrypoint: Manipulating stage timing so the UI lags the internal state
- Attacker controls: the timing of presence/absence around the consent signal
- Exploit idea: Compare the value driving the UI with the value used in `handle_user_qr_code` at the same instant.
- Invariant to test: Displayed consent state and enforced consent state are derived from one source of truth.
- Expected Immunefi impact: Biometric capture recorded under a policy the user did not consent to
- Fast validation: Integration test asserting UI signal and enforced policy are always the same value.
