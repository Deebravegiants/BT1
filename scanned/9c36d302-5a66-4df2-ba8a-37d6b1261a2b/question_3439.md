# Q3439: Unvalidated cross-process message in spawn_process (agent/process.rs)

## Question
Can an unprivileged attacker shape capture/scan data so the message `spawn_process` in [agentwire/src/agent/process.rs](agentwire/src/agent/process.rs) passes across the agent process boundary carries attacker-controlled sizes/offsets that the receiver trusts without validation?

## Target
- File/function: [agentwire/src/agent/process.rs](agentwire/src/agent/process.rs) -> `spawn_process` (function)
- Entrypoint: Capture and scan data flowing into the agent port
- Attacker controls: content and size of the data serialized into the message
- Exploit idea: Check whether `spawn_process` re-validates the message on the receiving side rather than trusting the sender.
- Invariant to test: Every message crossing a process boundary is validated on receipt, independent of sender.
- Expected Immunefi impact: Memory-safety or logic failure in the signup pipeline from routine capture data
- Fast validation: Fuzz the receive path of `spawn_process` with adversarial messages asserting validation.
