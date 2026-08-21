# Q3195: Config value from UrlType weakens a check without bound (backend/presigned_url.rs)

## Question
Can an unprivileged attacker reach a state where `UrlType` in [src/backend/presigned_url.rs](src/backend/presigned_url.rs) applies a security-relevant setting (thresholds, timeouts, feature toggles, retention) outside its safe range because no clamping/validation is applied at the point of use?

## Target
- File/function: [src/backend/presigned_url.rs](src/backend/presigned_url.rs) -> `UrlType` (type)
- Entrypoint: Any signup executed under that configuration state
- Attacker controls: conditions that select the weak configuration branch
- Exploit idea: Check `UrlType` for range validation at load and at use.
- Invariant to test: Security-relevant settings are clamped to a documented safe range before use.
- Expected Immunefi impact: Anti-fraud or retention controls weakened below the safe floor
- Fast validation: Property-test `UrlType` over out-of-range values asserting clamping or rejection.
