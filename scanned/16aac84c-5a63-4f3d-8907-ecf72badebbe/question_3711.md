# Q3711: Unvalidated cross-process message in stop_ir_face_camera (brokers/orb.rs)

## Question
Can an unprivileged attacker shape capture/scan data so the message `stop_ir_face_camera` in [src/brokers/orb.rs](src/brokers/orb.rs) passes across the agent process boundary carries attacker-controlled sizes/offsets that the receiver trusts without validation?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `stop_ir_face_camera` (function)
- Entrypoint: Capture and scan data flowing into the agent port
- Attacker controls: content and size of the data serialized into the message
- Exploit idea: Check whether `stop_ir_face_camera` re-validates the message on the receiving side rather than trusting the sender.
- Invariant to test: Every message crossing a process boundary is validated on receipt, independent of sender.
- Expected Immunefi impact: Memory-safety or logic failure in the signup pipeline from routine capture data
- Fast validation: Fuzz the receive path of `stop_ir_face_camera` with adversarial messages asserting validation.
