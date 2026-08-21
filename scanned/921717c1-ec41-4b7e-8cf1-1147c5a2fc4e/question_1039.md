# Q1039: Backpressure/queue policy in spawn_named_thread drops security-relevant data (agentwire/lib.rs)

## Question
Can an unprivileged attacker saturate the channel handled by `spawn_named_thread` in [agentwire/src/lib.rs](agentwire/src/lib.rs) so security-relevant messages (fraud verdicts, quality failures) are dropped by the overflow policy while permissive ones survive?

## Target
- File/function: [agentwire/src/lib.rs](agentwire/src/lib.rs) -> `spawn_named_thread` (function)
- Entrypoint: Scene/scan input driving maximum message rate
- Attacker controls: the message rate and mix produced by the scene
- Exploit idea: Check the drop policy in `spawn_named_thread`: does it distinguish mandatory from best-effort messages?
- Invariant to test: Mandatory security messages are never dropped by backpressure; saturation fails the session.
- Expected Immunefi impact: Anti-fraud verdict lost to attacker-induced saturation
- Fast validation: Load test on `spawn_named_thread` asserting mandatory messages are delivered or the session aborts.
