# Q1933: Config value from save_frame weakens a check without bound (agents/image_notary.rs)

## Question
Can an unprivileged attacker reach a state where `save_frame` in [src/agents/image_notary.rs](src/agents/image_notary.rs) applies a security-relevant setting (thresholds, timeouts, feature toggles, retention) outside its safe range because no clamping/validation is applied at the point of use?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `save_frame` (function)
- Entrypoint: Any signup executed under that configuration state
- Attacker controls: conditions that select the weak configuration branch
- Exploit idea: Check `save_frame` for range validation at load and at use.
- Invariant to test: Security-relevant settings are clamped to a documented safe range before use.
- Expected Immunefi impact: Anti-fraud or retention controls weakened below the safe floor
- Fast validation: Property-test `save_frame` over out-of-range values asserting clamping or rejection.
