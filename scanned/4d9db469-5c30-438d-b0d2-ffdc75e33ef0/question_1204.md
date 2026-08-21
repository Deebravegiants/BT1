# Q1204: Quadratic or unbounded work in join (network/mod.rs)

## Question
Can an unprivileged attacker present a payload whose structure (repeated separators, deep nesting, long runs) makes `join` in [src/network/mod.rs](src/network/mod.rs) do super-linear work per camera frame, starving the capture/agent loops for the duration of the attack?

## Target
- File/function: [src/network/mod.rs](src/network/mod.rs) -> `join` (function)
- Entrypoint: QR held continuously in front of the camera
- Attacker controls: payload structure repeated at camera frame rate
- Exploit idea: Measure `join` cost as payload structure scales and check for a per-frame budget or early-out.
- Invariant to test: Per-frame decode/parse cost is bounded independent of attacker-chosen payload structure.
- Expected Immunefi impact: Sustained degradation preventing signups on the targeted Orb
- Fast validation: Benchmark `join` across structured inputs and assert a hard upper bound on per-call time.
