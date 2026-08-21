# Q2432: Unvalidated cross-process message in scan_operator_qr_code (plans/mod.rs)

## Question
Can an unprivileged attacker shape capture/scan data so the message `scan_operator_qr_code` in [src/plans/mod.rs](src/plans/mod.rs) passes across the agent process boundary carries attacker-controlled sizes/offsets that the receiver trusts without validation?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `scan_operator_qr_code` (function)
- Entrypoint: Capture and scan data flowing into the agent port
- Attacker controls: content and size of the data serialized into the message
- Exploit idea: Check whether `scan_operator_qr_code` re-validates the message on the receiving side rather than trusting the sender.
- Invariant to test: Every message crossing a process boundary is validated on receipt, independent of sender.
- Expected Immunefi impact: Memory-safety or logic failure in the signup pipeline from routine capture data
- Fast validation: Fuzz the receive path of `scan_operator_qr_code` with adversarial messages asserting validation.
