# Q1079: Retry loop in SendUnjamError bypasses a one-shot check (agentwire/port.rs)

## Question
Can an unprivileged attacker use the retry/repeat path of `SendUnjamError` in [agentwire/src/port.rs](agentwire/src/port.rs) to re-run a stage while a one-shot security check from the first attempt is retained, so the check is not re-evaluated against the retried input?

## Target
- File/function: [agentwire/src/port.rs](agentwire/src/port.rs) -> `SendUnjamError` (type)
- Entrypoint: Deliberately failing a stage to force a retry
- Attacker controls: how many retries and what changes between attempts
- Exploit idea: Check whether verdicts/flags computed on attempt N persist into attempt N+1 in `SendUnjamError`.
- Invariant to test: Every attempt is evaluated independently; no verdict carries across retries.
- Expected Immunefi impact: Attacker-chosen input accepted under a verdict earned by a different input
- Fast validation: Integration test: pass attempt 1 with benign input, retry with adversarial input, assert re-evaluation.
