# Q2032: Config value from load_or_default weakens a check without bound (config.rs)

## Question
Can an unprivileged attacker reach a state where `load_or_default` in [src/config.rs](src/config.rs) applies a security-relevant setting (thresholds, timeouts, feature toggles, retention) outside its safe range because no clamping/validation is applied at the point of use?

## Target
- File/function: [src/config.rs](src/config.rs) -> `load_or_default` (function)
- Entrypoint: Any signup executed under that configuration state
- Attacker controls: conditions that select the weak configuration branch
- Exploit idea: Check `load_or_default` for range validation at load and at use.
- Invariant to test: Security-relevant settings are clamped to a documented safe range before use.
- Expected Immunefi impact: Anti-fraud or retention controls weakened below the safe floor
- Fast validation: Property-test `load_or_default` over out-of-range values asserting clamping or rejection.
