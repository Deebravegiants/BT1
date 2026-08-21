# Q1343: Retry loop in handle_qr_code bypasses a one-shot check (brokers/orb.rs)

## Question
Can an unprivileged attacker use the retry/repeat path of `handle_qr_code` in [src/brokers/orb.rs](src/brokers/orb.rs) to re-run a stage while a one-shot security check from the first attempt is retained, so the check is not re-evaluated against the retried input?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `handle_qr_code` (function)
- Entrypoint: Deliberately failing a stage to force a retry
- Attacker controls: how many retries and what changes between attempts
- Exploit idea: Check whether verdicts/flags computed on attempt N persist into attempt N+1 in `handle_qr_code`.
- Invariant to test: Every attempt is evaluated independently; no verdict carries across retries.
- Expected Immunefi impact: Attacker-chosen input accepted under a verdict earned by a different input
- Fast validation: Integration test: pass attempt 1 with benign input, retry with adversarial input, assert re-evaluation.
