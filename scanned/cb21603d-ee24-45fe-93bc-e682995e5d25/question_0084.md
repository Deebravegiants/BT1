# Q0084: Backpressure/queue policy in reset_mirror_calibration drops security-relevant data (plans/mod.rs)

## Question
Can an unprivileged attacker saturate the channel handled by `reset_mirror_calibration` in [src/plans/mod.rs](src/plans/mod.rs) so security-relevant messages (fraud verdicts, quality failures) are dropped by the overflow policy while permissive ones survive?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `reset_mirror_calibration` (function)
- Entrypoint: Scene/scan input driving maximum message rate
- Attacker controls: the message rate and mix produced by the scene
- Exploit idea: Check the drop policy in `reset_mirror_calibration`: does it distinguish mandatory from best-effort messages?
- Invariant to test: Mandatory security messages are never dropped by backpressure; saturation fails the session.
- Expected Immunefi impact: Anti-fraud verdict lost to attacker-induced saturation
- Fast validation: Load test on `reset_mirror_calibration` asserting mandatory messages are delivered or the session aborts.
