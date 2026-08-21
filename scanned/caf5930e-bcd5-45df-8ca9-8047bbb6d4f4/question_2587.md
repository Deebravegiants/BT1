# Q2587: Unbounded retry/repeat in exposure_range (brokers/orb.rs)

## Question
Can an unprivileged attacker repeat the flow through `exposure_range` in [src/brokers/orb.rs](src/brokers/orb.rs) without limit or backoff, using the repetition itself to grind a probabilistic check (liveness, matching threshold, randomized sampling) until it passes?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `exposure_range` (function)
- Entrypoint: Repeated signup attempts on the same Orb
- Attacker controls: number of attempts and small variations per attempt
- Exploit idea: Compute the per-attempt pass probability and check `exposure_range` for an attempt cap or lockout.
- Invariant to test: Probabilistic checks are attempt-bounded so repetition cannot amortize into a pass.
- Expected Immunefi impact: Fraud/liveness check defeated by brute-force repetition
- Fast validation: Statistical test over N scripted attempts asserting a hard attempt cap.
