# Q2609: Backpressure/queue policy in poll_extra drops security-relevant data (brokers/observer.rs)

## Question
Can an unprivileged attacker saturate the channel handled by `poll_extra` in [src/brokers/observer.rs](src/brokers/observer.rs) so security-relevant messages (fraud verdicts, quality failures) are dropped by the overflow policy while permissive ones survive?

## Target
- File/function: [src/brokers/observer.rs](src/brokers/observer.rs) -> `poll_extra` (function)
- Entrypoint: Scene/scan input driving maximum message rate
- Attacker controls: the message rate and mix produced by the scene
- Exploit idea: Check the drop policy in `poll_extra`: does it distinguish mandatory from best-effort messages?
- Invariant to test: Mandatory security messages are never dropped by backpressure; saturation fails the session.
- Expected Immunefi impact: Anti-fraud verdict lost to attacker-induced saturation
- Fast validation: Load test on `poll_extra` asserting mandatory messages are delivered or the session aborts.
