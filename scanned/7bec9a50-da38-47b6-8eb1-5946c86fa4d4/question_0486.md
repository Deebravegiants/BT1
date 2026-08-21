# Q0486: Cached verdict reused by iris_center_from_landmarks (agents/eye_pid_controller.rs)

## Question
Can an unprivileged attacker get `iris_center_from_landmarks` in [src/agents/eye_pid_controller.rs](src/agents/eye_pid_controller.rs) to reuse a cached verdict/score computed for an earlier frame, subject, or session, so the current capture inherits a pass it never earned?

## Target
- File/function: [src/agents/eye_pid_controller.rs](src/agents/eye_pid_controller.rs) -> `iris_center_from_landmarks` (function)
- Entrypoint: Repeating capture immediately after a passing capture
- Attacker controls: timing of the repeat relative to cache lifetime
- Exploit idea: Check the cache key in `iris_center_from_landmarks`: does it include session id, subject, and frame identity?
- Invariant to test: Verdict caches are keyed by session and input identity, and cleared at session end.
- Expected Immunefi impact: Anti-fraud verdict transplanted between subjects or sessions
- Fast validation: Integration test asserting a cache miss whenever session or subject changes.
