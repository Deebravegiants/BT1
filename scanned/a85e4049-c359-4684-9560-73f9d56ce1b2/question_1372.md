# Q1372: Backpressure/queue policy in stop_thermal_camera drops security-relevant data (brokers/orb.rs)

## Question
Can an unprivileged attacker saturate the channel handled by `stop_thermal_camera` in [src/brokers/orb.rs](src/brokers/orb.rs) so security-relevant messages (fraud verdicts, quality failures) are dropped by the overflow policy while permissive ones survive?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `stop_thermal_camera` (function)
- Entrypoint: Scene/scan input driving maximum message rate
- Attacker controls: the message rate and mix produced by the scene
- Exploit idea: Check the drop policy in `stop_thermal_camera`: does it distinguish mandatory from best-effort messages?
- Invariant to test: Mandatory security messages are never dropped by backpressure; saturation fails the session.
- Expected Immunefi impact: Anti-fraud verdict lost to attacker-induced saturation
- Fast validation: Load test on `stop_thermal_camera` asserting mandatory messages are delivered or the session aborts.
