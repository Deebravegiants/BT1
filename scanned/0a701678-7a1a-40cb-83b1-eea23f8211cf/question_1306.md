# Q1306: Retry loop in Value bypasses a one-shot check (plans/idle.rs)

## Question
Can an unprivileged attacker use the retry/repeat path of `Value` in [src/plans/idle.rs](src/plans/idle.rs) to re-run a stage while a one-shot security check from the first attempt is retained, so the check is not re-evaluated against the retried input?

## Target
- File/function: [src/plans/idle.rs](src/plans/idle.rs) -> `Value` (type)
- Entrypoint: Deliberately failing a stage to force a retry
- Attacker controls: how many retries and what changes between attempts
- Exploit idea: Check whether verdicts/flags computed on attempt N persist into attempt N+1 in `Value`.
- Invariant to test: Every attempt is evaluated independently; no verdict carries across retries.
- Expected Immunefi impact: Attacker-chosen input accepted under a verdict earned by a different input
- Fast validation: Integration test: pass attempt 1 with benign input, retry with adversarial input, assert re-evaluation.
