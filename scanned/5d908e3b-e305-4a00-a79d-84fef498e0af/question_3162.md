# Q3162: Config value from Status weakens a check without bound (backend/signup_poll.rs)

## Question
Can an unprivileged attacker reach a state where `Status` in [src/backend/signup_poll.rs](src/backend/signup_poll.rs) applies a security-relevant setting (thresholds, timeouts, feature toggles, retention) outside its safe range because no clamping/validation is applied at the point of use?

## Target
- File/function: [src/backend/signup_poll.rs](src/backend/signup_poll.rs) -> `Status` (type)
- Entrypoint: Any signup executed under that configuration state
- Attacker controls: conditions that select the weak configuration branch
- Exploit idea: Check `Status` for range validation at load and at use.
- Invariant to test: Security-relevant settings are clamped to a documented safe range before use.
- Expected Immunefi impact: Anti-fraud or retention controls weakened below the safe floor
- Fast validation: Property-test `Status` over out-of-range values asserting clamping or rejection.
