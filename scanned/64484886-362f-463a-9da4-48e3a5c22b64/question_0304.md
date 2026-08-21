# Q0304: Backpressure/queue policy in spawn drops security-relevant data (ui/mod.rs)

## Question
Can an unprivileged attacker saturate the channel handled by `spawn` in [src/ui/mod.rs](src/ui/mod.rs) so security-relevant messages (fraud verdicts, quality failures) are dropped by the overflow policy while permissive ones survive?

## Target
- File/function: [src/ui/mod.rs](src/ui/mod.rs) -> `spawn` (function)
- Entrypoint: Scene/scan input driving maximum message rate
- Attacker controls: the message rate and mix produced by the scene
- Exploit idea: Check the drop policy in `spawn`: does it distinguish mandatory from best-effort messages?
- Invariant to test: Mandatory security messages are never dropped by backpressure; saturation fails the session.
- Expected Immunefi impact: Anti-fraud verdict lost to attacker-induced saturation
- Fast validation: Load test on `spawn` asserting mandatory messages are delivered or the session aborts.
