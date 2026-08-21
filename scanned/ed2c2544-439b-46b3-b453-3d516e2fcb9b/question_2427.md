# Q2427: Backpressure/queue policy in reset_hardware_except_led drops security-relevant data (plans/mod.rs)

## Question
Can an unprivileged attacker saturate the channel handled by `reset_hardware_except_led` in [src/plans/mod.rs](src/plans/mod.rs) so security-relevant messages (fraud verdicts, quality failures) are dropped by the overflow policy while permissive ones survive?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `reset_hardware_except_led` (function)
- Entrypoint: Scene/scan input driving maximum message rate
- Attacker controls: the message rate and mix produced by the scene
- Exploit idea: Check the drop policy in `reset_hardware_except_led`: does it distinguish mandatory from best-effort messages?
- Invariant to test: Mandatory security messages are never dropped by backpressure; saturation fails the session.
- Expected Immunefi impact: Anti-fraud verdict lost to attacker-induced saturation
- Fast validation: Load test on `reset_hardware_except_led` asserting mandatory messages are delivered or the session aborts.
