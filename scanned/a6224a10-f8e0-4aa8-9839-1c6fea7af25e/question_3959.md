# Q3959: Cached verdict reused by fraud_checks_strict (plans/fraud_check.rs)

## Question
Can an unprivileged attacker get `fraud_checks_strict` in [src/plans/fraud_check.rs](src/plans/fraud_check.rs) to reuse a cached verdict/score computed for an earlier frame, subject, or session, so the current capture inherits a pass it never earned?

## Target
- File/function: [src/plans/fraud_check.rs](src/plans/fraud_check.rs) -> `fraud_checks_strict` (function)
- Entrypoint: Repeating capture immediately after a passing capture
- Attacker controls: timing of the repeat relative to cache lifetime
- Exploit idea: Check the cache key in `fraud_checks_strict`: does it include session id, subject, and frame identity?
- Invariant to test: Verdict caches are keyed by session and input identity, and cleared at session end.
- Expected Immunefi impact: Anti-fraud verdict transplanted between subjects or sessions
- Fast validation: Integration test asserting a cache miss whenever session or subject changes.
