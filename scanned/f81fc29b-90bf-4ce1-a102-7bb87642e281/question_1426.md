# Q1426: UI/consent state desynchronized from handle_mcu_battery_capacity (brokers/observer.rs)

## Question
Can an unprivileged attacker make the state signalled to the user by the UI diverge from the state actually used by `handle_mcu_battery_capacity` in [src/brokers/observer.rs](src/brokers/observer.rs), so the person being captured consents to one thing while a different policy/identity is recorded?

## Target
- File/function: [src/brokers/observer.rs](src/brokers/observer.rs) -> `handle_mcu_battery_capacity` (function)
- Entrypoint: Manipulating stage timing so the UI lags the internal state
- Attacker controls: the timing of presence/absence around the consent signal
- Exploit idea: Compare the value driving the UI with the value used in `handle_mcu_battery_capacity` at the same instant.
- Invariant to test: Displayed consent state and enforced consent state are derived from one source of truth.
- Expected Immunefi impact: Biometric capture recorded under a policy the user did not consent to
- Fast validation: Integration test asserting UI signal and enforced policy are always the same value.
