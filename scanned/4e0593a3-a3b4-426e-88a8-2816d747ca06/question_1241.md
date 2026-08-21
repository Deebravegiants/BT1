# Q1241: Retry loop in ci_hacks bypasses a one-shot check (plans/mod.rs)

## Question
Can an unprivileged attacker use the retry/repeat path of `ci_hacks` in [src/plans/mod.rs](src/plans/mod.rs) to re-run a stage while a one-shot security check from the first attempt is retained, so the check is not re-evaluated against the retried input?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `ci_hacks` (function)
- Entrypoint: Deliberately failing a stage to force a retry
- Attacker controls: how many retries and what changes between attempts
- Exploit idea: Check whether verdicts/flags computed on attempt N persist into attempt N+1 in `ci_hacks`.
- Invariant to test: Every attempt is evaluated independently; no verdict carries across retries.
- Expected Immunefi impact: Attacker-chosen input accepted under a verdict earned by a different input
- Fast validation: Integration test: pass attempt 1 with benign input, retry with adversarial input, assert re-evaluation.
