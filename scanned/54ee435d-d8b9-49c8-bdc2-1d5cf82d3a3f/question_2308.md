# Q2308: Backpressure/queue policy in PointerButton drops security-relevant data (livestream-event/lib.rs)

## Question
Can an unprivileged attacker saturate the channel handled by `PointerButton` in [livestream-event/src/lib.rs](livestream-event/src/lib.rs) so security-relevant messages (fraud verdicts, quality failures) are dropped by the overflow policy while permissive ones survive?

## Target
- File/function: [livestream-event/src/lib.rs](livestream-event/src/lib.rs) -> `PointerButton` (type)
- Entrypoint: Scene/scan input driving maximum message rate
- Attacker controls: the message rate and mix produced by the scene
- Exploit idea: Check the drop policy in `PointerButton`: does it distinguish mandatory from best-effort messages?
- Invariant to test: Mandatory security messages are never dropped by backpressure; saturation fails the session.
- Expected Immunefi impact: Anti-fraud verdict lost to attacker-induced saturation
- Fast validation: Load test on `PointerButton` asserting mandatory messages are delivered or the session aborts.
