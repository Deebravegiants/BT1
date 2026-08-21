# Q3656: Unbounded retry/repeat in rgb_net_warmup (plans/warmup.rs)

## Question
Can an unprivileged attacker repeat the flow through `rgb_net_warmup` in [src/plans/warmup.rs](src/plans/warmup.rs) without limit or backoff, using the repetition itself to grind a probabilistic check (liveness, matching threshold, randomized sampling) until it passes?

## Target
- File/function: [src/plans/warmup.rs](src/plans/warmup.rs) -> `rgb_net_warmup` (function)
- Entrypoint: Repeated signup attempts on the same Orb
- Attacker controls: number of attempts and small variations per attempt
- Exploit idea: Compute the per-attempt pass probability and check `rgb_net_warmup` for an attempt cap or lockout.
- Invariant to test: Probabilistic checks are attempt-bounded so repetition cannot amortize into a pass.
- Expected Immunefi impact: Fraud/liveness check defeated by brute-force repetition
- Fast validation: Statistical test over N scripted attempts asserting a hard attempt cap.
