# Q1940: Config value from Input weakens a check without bound (agents/image_notary.rs)

## Question
Can an unprivileged attacker reach a state where `Input` in [src/agents/image_notary.rs](src/agents/image_notary.rs) applies a security-relevant setting (thresholds, timeouts, feature toggles, retention) outside its safe range because no clamping/validation is applied at the point of use?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `Input` (type)
- Entrypoint: Any signup executed under that configuration state
- Attacker controls: conditions that select the weak configuration branch
- Exploit idea: Check `Input` for range validation at load and at use.
- Invariant to test: Security-relevant settings are clamped to a documented safe range before use.
- Expected Immunefi impact: Anti-fraud or retention controls weakened below the safe floor
- Fast validation: Property-test `Input` over out-of-range values asserting clamping or rejection.
