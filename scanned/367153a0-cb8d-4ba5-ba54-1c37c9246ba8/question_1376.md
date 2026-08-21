# Q1376: Unvalidated cross-process message in stop_distance (brokers/orb.rs)

## Question
Can an unprivileged attacker shape capture/scan data so the message `stop_distance` in [src/brokers/orb.rs](src/brokers/orb.rs) passes across the agent process boundary carries attacker-controlled sizes/offsets that the receiver trusts without validation?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `stop_distance` (function)
- Entrypoint: Capture and scan data flowing into the agent port
- Attacker controls: content and size of the data serialized into the message
- Exploit idea: Check whether `stop_distance` re-validates the message on the receiving side rather than trusting the sender.
- Invariant to test: Every message crossing a process boundary is validated on receipt, independent of sender.
- Expected Immunefi impact: Memory-safety or logic failure in the signup pipeline from routine capture data
- Fast validation: Fuzz the receive path of `stop_distance` with adversarial messages asserting validation.
