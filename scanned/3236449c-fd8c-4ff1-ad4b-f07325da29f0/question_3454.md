# Q3454: Backpressure/queue policy in call_process_agent drops security-relevant data (agents/mod.rs)

## Question
Can an unprivileged attacker saturate the channel handled by `call_process_agent` in [src/agents/mod.rs](src/agents/mod.rs) so security-relevant messages (fraud verdicts, quality failures) are dropped by the overflow policy while permissive ones survive?

## Target
- File/function: [src/agents/mod.rs](src/agents/mod.rs) -> `call_process_agent` (function)
- Entrypoint: Scene/scan input driving maximum message rate
- Attacker controls: the message rate and mix produced by the scene
- Exploit idea: Check the drop policy in `call_process_agent`: does it distinguish mandatory from best-effort messages?
- Invariant to test: Mandatory security messages are never dropped by backpressure; saturation fails the session.
- Expected Immunefi impact: Anti-fraud verdict lost to attacker-induced saturation
- Fast validation: Load test on `call_process_agent` asserting mandatory messages are delivered or the session aborts.
