# Q2324: Unvalidated cross-process message in send_blocking (orb-relay-client/client.rs)

## Question
Can an unprivileged attacker shape capture/scan data so the message `send_blocking` in [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) passes across the agent process boundary carries attacker-controlled sizes/offsets that the receiver trusts without validation?

## Target
- File/function: [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) -> `send_blocking` (function)
- Entrypoint: Capture and scan data flowing into the agent port
- Attacker controls: content and size of the data serialized into the message
- Exploit idea: Check whether `send_blocking` re-validates the message on the receiving side rather than trusting the sender.
- Invariant to test: Every message crossing a process boundary is validated on receipt, independent of sender.
- Expected Immunefi impact: Memory-safety or logic failure in the signup pipeline from routine capture data
- Fast validation: Fuzz the receive path of `send_blocking` with adversarial messages asserting validation.
