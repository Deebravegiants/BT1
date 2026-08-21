# Q0263: Unvalidated cross-process message in is_fan_control_active (brokers/observer.rs)

## Question
Can an unprivileged attacker shape capture/scan data so the message `is_fan_control_active` in [src/brokers/observer.rs](src/brokers/observer.rs) passes across the agent process boundary carries attacker-controlled sizes/offsets that the receiver trusts without validation?

## Target
- File/function: [src/brokers/observer.rs](src/brokers/observer.rs) -> `is_fan_control_active` (function)
- Entrypoint: Capture and scan data flowing into the agent port
- Attacker controls: content and size of the data serialized into the message
- Exploit idea: Check whether `is_fan_control_active` re-validates the message on the receiving side rather than trusting the sender.
- Invariant to test: Every message crossing a process boundary is validated on receipt, independent of sender.
- Expected Immunefi impact: Memory-safety or logic failure in the signup pipeline from routine capture data
- Fast validation: Fuzz the receive path of `is_fan_control_active` with adversarial messages asserting validation.
