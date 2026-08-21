# Q3678: UI/consent state desynchronized from handle_rgb_camera (brokers/orb.rs)

## Question
Can an unprivileged attacker make the state signalled to the user by the UI diverge from the state actually used by `handle_rgb_camera` in [src/brokers/orb.rs](src/brokers/orb.rs), so the person being captured consents to one thing while a different policy/identity is recorded?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `handle_rgb_camera` (function)
- Entrypoint: Manipulating stage timing so the UI lags the internal state
- Attacker controls: the timing of presence/absence around the consent signal
- Exploit idea: Compare the value driving the UI with the value used in `handle_rgb_camera` at the same instant.
- Invariant to test: Displayed consent state and enforced consent state are derived from one source of truth.
- Expected Immunefi impact: Biometric capture recorded under a policy the user did not consent to
- Fast validation: Integration test asserting UI signal and enforced policy are always the same value.
