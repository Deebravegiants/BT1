# Q2249: Backpressure/queue policy in CreateSharedMemoryError drops security-relevant data (agentwire/port.rs)

## Question
Can an unprivileged attacker saturate the channel handled by `CreateSharedMemoryError` in [agentwire/src/port.rs](agentwire/src/port.rs) so security-relevant messages (fraud verdicts, quality failures) are dropped by the overflow policy while permissive ones survive?

## Target
- File/function: [agentwire/src/port.rs](agentwire/src/port.rs) -> `CreateSharedMemoryError` (type)
- Entrypoint: Scene/scan input driving maximum message rate
- Attacker controls: the message rate and mix produced by the scene
- Exploit idea: Check the drop policy in `CreateSharedMemoryError`: does it distinguish mandatory from best-effort messages?
- Invariant to test: Mandatory security messages are never dropped by backpressure; saturation fails the session.
- Expected Immunefi impact: Anti-fraud verdict lost to attacker-induced saturation
- Fast validation: Load test on `CreateSharedMemoryError` asserting mandatory messages are delivered or the session aborts.
