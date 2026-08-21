# Q3523: Quadratic or unbounded work in run_pre (qr_scan/mod.rs)

## Question
Can an unprivileged attacker present a payload whose structure (repeated separators, deep nesting, long runs) makes `run_pre` in [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) do super-linear work per camera frame, starving the capture/agent loops for the duration of the attack?

## Target
- File/function: [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) -> `run_pre` (function)
- Entrypoint: QR held continuously in front of the camera
- Attacker controls: payload structure repeated at camera frame rate
- Exploit idea: Measure `run_pre` cost as payload structure scales and check for a per-frame budget or early-out.
- Invariant to test: Per-frame decode/parse cost is bounded independent of attacker-chosen payload structure.
- Expected Immunefi impact: Sustained degradation preventing signups on the targeted Orb
- Fast validation: Benchmark `run_pre` across structured inputs and assert a hard upper bound on per-call time.
