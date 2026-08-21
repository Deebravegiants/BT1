# Q1092: Backpressure/queue policy in keep_file_descriptors drops security-relevant data (agent/process.rs)

## Question
Can an unprivileged attacker saturate the channel handled by `keep_file_descriptors` in [agentwire/src/agent/process.rs](agentwire/src/agent/process.rs) so security-relevant messages (fraud verdicts, quality failures) are dropped by the overflow policy while permissive ones survive?

## Target
- File/function: [agentwire/src/agent/process.rs](agentwire/src/agent/process.rs) -> `keep_file_descriptors` (function)
- Entrypoint: Scene/scan input driving maximum message rate
- Attacker controls: the message rate and mix produced by the scene
- Exploit idea: Check the drop policy in `keep_file_descriptors`: does it distinguish mandatory from best-effort messages?
- Invariant to test: Mandatory security messages are never dropped by backpressure; saturation fails the session.
- Expected Immunefi impact: Anti-fraud verdict lost to attacker-induced saturation
- Fast validation: Load test on `keep_file_descriptors` asserting mandatory messages are delivered or the session aborts.
