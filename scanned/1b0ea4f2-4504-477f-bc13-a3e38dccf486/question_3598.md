# Q3598: Unvalidated cross-process message in reset_hardware (plans/mod.rs)

## Question
Can an unprivileged attacker shape capture/scan data so the message `reset_hardware` in [src/plans/mod.rs](src/plans/mod.rs) passes across the agent process boundary carries attacker-controlled sizes/offsets that the receiver trusts without validation?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `reset_hardware` (function)
- Entrypoint: Capture and scan data flowing into the agent port
- Attacker controls: content and size of the data serialized into the message
- Exploit idea: Check whether `reset_hardware` re-validates the message on the receiving side rather than trusting the sender.
- Invariant to test: Every message crossing a process boundary is validated on receipt, independent of sender.
- Expected Immunefi impact: Memory-safety or logic failure in the signup pipeline from routine capture data
- Fast validation: Fuzz the receive path of `reset_hardware` with adversarial messages asserting validation.
