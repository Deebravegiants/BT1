# Q1456: Unbounded retry/repeat in handle_double_press (brokers/observer.rs)

## Question
Can an unprivileged attacker repeat the flow through `handle_double_press` in [src/brokers/observer.rs](src/brokers/observer.rs) without limit or backoff, using the repetition itself to grind a probabilistic check (liveness, matching threshold, randomized sampling) until it passes?

## Target
- File/function: [src/brokers/observer.rs](src/brokers/observer.rs) -> `handle_double_press` (function)
- Entrypoint: Repeated signup attempts on the same Orb
- Attacker controls: number of attempts and small variations per attempt
- Exploit idea: Compute the per-attempt pass probability and check `handle_double_press` for an attempt cap or lockout.
- Invariant to test: Probabilistic checks are attempt-bounded so repetition cannot amortize into a pass.
- Expected Immunefi impact: Fraud/liveness check defeated by brute-force repetition
- Fast validation: Statistical test over N scripted attempts asserting a hard attempt cap.
