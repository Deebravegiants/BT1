# Q2228: Unbounded retry/repeat in from_fd (agentwire/port.rs)

## Question
Can an unprivileged attacker repeat the flow through `from_fd` in [agentwire/src/port.rs](agentwire/src/port.rs) without limit or backoff, using the repetition itself to grind a probabilistic check (liveness, matching threshold, randomized sampling) until it passes?

## Target
- File/function: [agentwire/src/port.rs](agentwire/src/port.rs) -> `from_fd` (function)
- Entrypoint: Repeated signup attempts on the same Orb
- Attacker controls: number of attempts and small variations per attempt
- Exploit idea: Compute the per-attempt pass probability and check `from_fd` for an attempt cap or lockout.
- Invariant to test: Probabilistic checks are attempt-bounded so repetition cannot amortize into a pass.
- Expected Immunefi impact: Fraud/liveness check defeated by brute-force repetition
- Fast validation: Statistical test over N scripted attempts asserting a hard attempt cap.
