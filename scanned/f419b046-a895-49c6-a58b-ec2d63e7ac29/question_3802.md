# Q3802: Backpressure/queue policy in log_mcu_motor_range drops security-relevant data (brokers/observer.rs)

## Question
Can an unprivileged attacker saturate the channel handled by `log_mcu_motor_range` in [src/brokers/observer.rs](src/brokers/observer.rs) so security-relevant messages (fraud verdicts, quality failures) are dropped by the overflow policy while permissive ones survive?

## Target
- File/function: [src/brokers/observer.rs](src/brokers/observer.rs) -> `log_mcu_motor_range` (function)
- Entrypoint: Scene/scan input driving maximum message rate
- Attacker controls: the message rate and mix produced by the scene
- Exploit idea: Check the drop policy in `log_mcu_motor_range`: does it distinguish mandatory from best-effort messages?
- Invariant to test: Mandatory security messages are never dropped by backpressure; saturation fails the session.
- Expected Immunefi impact: Anti-fraud verdict lost to attacker-induced saturation
- Fast validation: Load test on `log_mcu_motor_range` asserting mandatory messages are delivered or the session aborts.
