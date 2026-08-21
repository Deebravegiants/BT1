# Q1804: Version/model mismatch unchecked in rgb_net_estimate (python/rgb_net.rs)

## Question
Can an unprivileged attacker benefit from `rgb_net_estimate` in [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) not verifying that the model/pipeline version producing a result matches the version the consuming check expects, so scores are interpreted on the wrong scale?

## Target
- File/function: [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) -> `rgb_net_estimate` (function)
- Entrypoint: Any signup executed while a version skew exists
- Attacker controls: timing of the signup relative to component versions in use
- Exploit idea: Check `rgb_net_estimate` for a version guard between producer and consumer of the score.
- Invariant to test: Scores carry and enforce a version tag matching the interpreting check.
- Expected Immunefi impact: Fraud/quality thresholds silently misapplied, admitting rejectable captures
- Fast validation: Unit-test `rgb_net_estimate` with a mismatched version tag asserting a hard error.
