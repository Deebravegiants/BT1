# Q1321: Retry loop in Plan bypasses a one-shot check (plans/detect_face.rs)

## Question
Can an unprivileged attacker use the retry/repeat path of `Plan` in [src/plans/detect_face.rs](src/plans/detect_face.rs) to re-run a stage while a one-shot security check from the first attempt is retained, so the check is not re-evaluated against the retried input?

## Target
- File/function: [src/plans/detect_face.rs](src/plans/detect_face.rs) -> `Plan` (type)
- Entrypoint: Deliberately failing a stage to force a retry
- Attacker controls: how many retries and what changes between attempts
- Exploit idea: Check whether verdicts/flags computed on attempt N persist into attempt N+1 in `Plan`.
- Invariant to test: Every attempt is evaluated independently; no verdict carries across retries.
- Expected Immunefi impact: Attacker-chosen input accepted under a verdict earned by a different input
- Fast validation: Integration test: pass attempt 1 with benign input, retry with adversarial input, assert re-evaluation.
