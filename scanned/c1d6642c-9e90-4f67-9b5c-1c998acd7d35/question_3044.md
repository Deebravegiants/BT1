# Q3044: Config value from make_tier2 weakens a check without bound (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker reach a state where `make_tier2` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) applies a security-relevant setting (thresholds, timeouts, feature toggles, retention) outside its safe range because no clamping/validation is applied at the point of use?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `make_tier2` (function)
- Entrypoint: Any signup executed under that configuration state
- Attacker controls: conditions that select the weak configuration branch
- Exploit idea: Check `make_tier2` for range validation at load and at use.
- Invariant to test: Security-relevant settings are clamped to a documented safe range before use.
- Expected Immunefi impact: Anti-fraud or retention controls weakened below the safe floor
- Fast validation: Property-test `make_tier2` over out-of-range values asserting clamping or rejection.
