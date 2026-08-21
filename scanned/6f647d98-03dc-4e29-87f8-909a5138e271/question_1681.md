# Q1681: Cached verdict reused by run (agents/thermal.rs)

## Question
Can an unprivileged attacker get `run` in [src/agents/thermal.rs](src/agents/thermal.rs) to reuse a cached verdict/score computed for an earlier frame, subject, or session, so the current capture inherits a pass it never earned?

## Target
- File/function: [src/agents/thermal.rs](src/agents/thermal.rs) -> `run` (function)
- Entrypoint: Repeating capture immediately after a passing capture
- Attacker controls: timing of the repeat relative to cache lifetime
- Exploit idea: Check the cache key in `run`: does it include session id, subject, and frame identity?
- Invariant to test: Verdict caches are keyed by session and input identity, and cleared at session end.
- Expected Immunefi impact: Anti-fraud verdict transplanted between subjects or sessions
- Fast validation: Integration test asserting a cache miss whenever session or subject changes.
