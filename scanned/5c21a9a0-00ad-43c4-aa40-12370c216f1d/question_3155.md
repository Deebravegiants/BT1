# Q3155: Config value from IrisData weakens a check without bound (backend/signup_post.rs)

## Question
Can an unprivileged attacker reach a state where `IrisData` in [src/backend/signup_post.rs](src/backend/signup_post.rs) applies a security-relevant setting (thresholds, timeouts, feature toggles, retention) outside its safe range because no clamping/validation is applied at the point of use?

## Target
- File/function: [src/backend/signup_post.rs](src/backend/signup_post.rs) -> `IrisData` (type)
- Entrypoint: Any signup executed under that configuration state
- Attacker controls: conditions that select the weak configuration branch
- Exploit idea: Check `IrisData` for range validation at load and at use.
- Invariant to test: Security-relevant settings are clamped to a documented safe range before use.
- Expected Immunefi impact: Anti-fraud or retention controls weakened below the safe floor
- Fast validation: Property-test `IrisData` over out-of-range values asserting clamping or rejection.
