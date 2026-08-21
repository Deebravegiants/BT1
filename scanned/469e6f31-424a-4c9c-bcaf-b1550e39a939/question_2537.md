# Q2537: Unbounded retry/repeat in stop_ir_eye_camera (brokers/orb.rs)

## Question
Can an unprivileged attacker repeat the flow through `stop_ir_eye_camera` in [src/brokers/orb.rs](src/brokers/orb.rs) without limit or backoff, using the repetition itself to grind a probabilistic check (liveness, matching threshold, randomized sampling) until it passes?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `stop_ir_eye_camera` (function)
- Entrypoint: Repeated signup attempts on the same Orb
- Attacker controls: number of attempts and small variations per attempt
- Exploit idea: Compute the per-attempt pass probability and check `stop_ir_eye_camera` for an attempt cap or lockout.
- Invariant to test: Probabilistic checks are attempt-bounded so repetition cannot amortize into a pass.
- Expected Immunefi impact: Fraud/liveness check defeated by brute-force repetition
- Fast validation: Statistical test over N scripted attempts asserting a hard attempt cap.
