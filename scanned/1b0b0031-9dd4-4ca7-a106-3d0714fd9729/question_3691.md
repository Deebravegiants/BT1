# Q3691: Backpressure/queue policy in build drops security-relevant data (brokers/orb.rs)

## Question
Can an unprivileged attacker saturate the channel handled by `build` in [src/brokers/orb.rs](src/brokers/orb.rs) so security-relevant messages (fraud verdicts, quality failures) are dropped by the overflow policy while permissive ones survive?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `build` (function)
- Entrypoint: Scene/scan input driving maximum message rate
- Attacker controls: the message rate and mix produced by the scene
- Exploit idea: Check the drop policy in `build`: does it distinguish mandatory from best-effort messages?
- Invariant to test: Mandatory security messages are never dropped by backpressure; saturation fails the session.
- Expected Immunefi impact: Anti-fraud verdict lost to attacker-induced saturation
- Fast validation: Load test on `build` asserting mandatory messages are delivered or the session aborts.
