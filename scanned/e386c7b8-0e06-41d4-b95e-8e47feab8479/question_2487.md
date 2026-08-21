# Q2487: Unbounded retry/repeat in wait_until_cpu_is_not_overloaded (plans/warmup.rs)

## Question
Can an unprivileged attacker repeat the flow through `wait_until_cpu_is_not_overloaded` in [src/plans/warmup.rs](src/plans/warmup.rs) without limit or backoff, using the repetition itself to grind a probabilistic check (liveness, matching threshold, randomized sampling) until it passes?

## Target
- File/function: [src/plans/warmup.rs](src/plans/warmup.rs) -> `wait_until_cpu_is_not_overloaded` (function)
- Entrypoint: Repeated signup attempts on the same Orb
- Attacker controls: number of attempts and small variations per attempt
- Exploit idea: Compute the per-attempt pass probability and check `wait_until_cpu_is_not_overloaded` for an attempt cap or lockout.
- Invariant to test: Probabilistic checks are attempt-bounded so repetition cannot amortize into a pass.
- Expected Immunefi impact: Fraud/liveness check defeated by brute-force repetition
- Fast validation: Statistical test over N scripted attempts asserting a hard attempt cap.
