# Q1860: Config value from run weakens a check without bound (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker reach a state where `run` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) applies a security-relevant setting (thresholds, timeouts, feature toggles, retention) outside its safe range because no clamping/validation is applied at the point of use?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `run` (function)
- Entrypoint: Any signup executed under that configuration state
- Attacker controls: conditions that select the weak configuration branch
- Exploit idea: Check `run` for range validation at load and at use.
- Invariant to test: Security-relevant settings are clamped to a documented safe range before use.
- Expected Immunefi impact: Anti-fraud or retention controls weakened below the safe floor
- Fast validation: Property-test `run` over out-of-range values asserting clamping or rejection.
