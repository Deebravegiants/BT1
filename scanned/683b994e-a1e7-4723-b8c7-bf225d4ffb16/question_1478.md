# Q1478: Retry loop in QrScanSchema bypasses a one-shot check (ui/mod.rs)

## Question
Can an unprivileged attacker use the retry/repeat path of `QrScanSchema` in [src/ui/mod.rs](src/ui/mod.rs) to re-run a stage while a one-shot security check from the first attempt is retained, so the check is not re-evaluated against the retried input?

## Target
- File/function: [src/ui/mod.rs](src/ui/mod.rs) -> `QrScanSchema` (type)
- Entrypoint: Deliberately failing a stage to force a retry
- Attacker controls: how many retries and what changes between attempts
- Exploit idea: Check whether verdicts/flags computed on attempt N persist into attempt N+1 in `QrScanSchema`.
- Invariant to test: Every attempt is evaluated independently; no verdict carries across retries.
- Expected Immunefi impact: Attacker-chosen input accepted under a verdict earned by a different input
- Fast validation: Integration test: pass attempt 1 with benign input, retry with adversarial input, assert re-evaluation.
