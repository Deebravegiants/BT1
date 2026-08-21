# Q2466: Unbounded retry/repeat in is_success (plans/enroll_user.rs)

## Question
Can an unprivileged attacker repeat the flow through `is_success` in [src/plans/enroll_user.rs](src/plans/enroll_user.rs) without limit or backoff, using the repetition itself to grind a probabilistic check (liveness, matching threshold, randomized sampling) until it passes?

## Target
- File/function: [src/plans/enroll_user.rs](src/plans/enroll_user.rs) -> `is_success` (function)
- Entrypoint: Repeated signup attempts on the same Orb
- Attacker controls: number of attempts and small variations per attempt
- Exploit idea: Compute the per-attempt pass probability and check `is_success` for an attempt cap or lockout.
- Invariant to test: Probabilistic checks are attempt-bounded so repetition cannot amortize into a pass.
- Expected Immunefi impact: Fraud/liveness check defeated by brute-force repetition
- Fast validation: Statistical test over N scripted attempts asserting a hard attempt cap.
