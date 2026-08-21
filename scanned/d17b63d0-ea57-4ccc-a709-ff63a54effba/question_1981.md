# Q1981: Config value from format_eye_pipeline weakens a check without bound (backend/signup_post.rs)

## Question
Can an unprivileged attacker reach a state where `format_eye_pipeline` in [src/backend/signup_post.rs](src/backend/signup_post.rs) applies a security-relevant setting (thresholds, timeouts, feature toggles, retention) outside its safe range because no clamping/validation is applied at the point of use?

## Target
- File/function: [src/backend/signup_post.rs](src/backend/signup_post.rs) -> `format_eye_pipeline` (function)
- Entrypoint: Any signup executed under that configuration state
- Attacker controls: conditions that select the weak configuration branch
- Exploit idea: Check `format_eye_pipeline` for range validation at load and at use.
- Invariant to test: Security-relevant settings are clamped to a documented safe range before use.
- Expected Immunefi impact: Anti-fraud or retention controls weakened below the safe floor
- Fast validation: Property-test `format_eye_pipeline` over out-of-range values asserting clamping or rejection.
