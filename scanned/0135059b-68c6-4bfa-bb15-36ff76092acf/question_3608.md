# Q3608: Unbounded retry/repeat in detect_face (plans/mod.rs)

## Question
Can an unprivileged attacker repeat the flow through `detect_face` in [src/plans/mod.rs](src/plans/mod.rs) without limit or backoff, using the repetition itself to grind a probabilistic check (liveness, matching threshold, randomized sampling) until it passes?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `detect_face` (function)
- Entrypoint: Repeated signup attempts on the same Orb
- Attacker controls: number of attempts and small variations per attempt
- Exploit idea: Compute the per-attempt pass probability and check `detect_face` for an attempt cap or lockout.
- Invariant to test: Probabilistic checks are attempt-bounded so repetition cannot amortize into a pass.
- Expected Immunefi impact: Fraud/liveness check defeated by brute-force repetition
- Fast validation: Statistical test over N scripted attempts asserting a hard attempt cap.
