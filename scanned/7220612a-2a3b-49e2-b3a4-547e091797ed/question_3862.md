# Q3862: Cached verdict reused by handle_rgb_net (biometric_capture/focus_sweep.rs)

## Question
Can an unprivileged attacker get `handle_rgb_net` in [src/plans/biometric_capture/focus_sweep.rs](src/plans/biometric_capture/focus_sweep.rs) to reuse a cached verdict/score computed for an earlier frame, subject, or session, so the current capture inherits a pass it never earned?

## Target
- File/function: [src/plans/biometric_capture/focus_sweep.rs](src/plans/biometric_capture/focus_sweep.rs) -> `handle_rgb_net` (function)
- Entrypoint: Repeating capture immediately after a passing capture
- Attacker controls: timing of the repeat relative to cache lifetime
- Exploit idea: Check the cache key in `handle_rgb_net`: does it include session id, subject, and frame identity?
- Invariant to test: Verdict caches are keyed by session and input identity, and cleared at session end.
- Expected Immunefi impact: Anti-fraud verdict transplanted between subjects or sessions
- Fast validation: Integration test asserting a cache miss whenever session or subject changes.
