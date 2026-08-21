# Q3508: Unbounded retry/repeat in TokenAuth (orb-relay-client/client.rs)

## Question
Can an unprivileged attacker repeat the flow through `TokenAuth` in [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) without limit or backoff, using the repetition itself to grind a probabilistic check (liveness, matching threshold, randomized sampling) until it passes?

## Target
- File/function: [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) -> `TokenAuth` (type)
- Entrypoint: Repeated signup attempts on the same Orb
- Attacker controls: number of attempts and small variations per attempt
- Exploit idea: Compute the per-attempt pass probability and check `TokenAuth` for an attempt cap or lockout.
- Invariant to test: Probabilistic checks are attempt-bounded so repetition cannot amortize into a pass.
- Expected Immunefi impact: Fraud/liveness check defeated by brute-force repetition
- Fast validation: Statistical test over N scripted attempts asserting a hard attempt cap.
