# Q3432: Unvalidated cross-process message in is_enabled (agent/mod.rs)

## Question
Can an unprivileged attacker shape capture/scan data so the message `is_enabled` in [agentwire/src/agent/mod.rs](agentwire/src/agent/mod.rs) passes across the agent process boundary carries attacker-controlled sizes/offsets that the receiver trusts without validation?

## Target
- File/function: [agentwire/src/agent/mod.rs](agentwire/src/agent/mod.rs) -> `is_enabled` (function)
- Entrypoint: Capture and scan data flowing into the agent port
- Attacker controls: content and size of the data serialized into the message
- Exploit idea: Check whether `is_enabled` re-validates the message on the receiving side rather than trusting the sender.
- Invariant to test: Every message crossing a process boundary is validated on receipt, independent of sender.
- Expected Immunefi impact: Memory-safety or logic failure in the signup pipeline from routine capture data
- Fast validation: Fuzz the receive path of `is_enabled` with adversarial messages asserting validation.
