# Q3513: Deserialization boundary in Command lacks a size cap (orb-relay-client/client.rs)

## Question
Can an unprivileged attacker cause `Command` in [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) to decode a message whose declared size is attacker-influenced and unbounded, allocating far beyond available memory?

## Target
- File/function: [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) -> `Command` (type)
- Entrypoint: Data whose size flows from capture/scan into the message
- Attacker controls: the size-determining content of the input
- Exploit idea: Check `Command` for a maximum message size enforced before allocation.
- Invariant to test: Message size limits are enforced before any allocation.
- Expected Immunefi impact: Memory exhaustion from routine attacker-shaped input
- Fast validation: Fuzz `Command` with oversized length headers asserting the cap is enforced.
