# Q1140: Deserialization boundary in into_payload lacks a size cap (orb-relay-client/lib.rs)

## Question
Can an unprivileged attacker cause `into_payload` in [orb-relay-client/src/lib.rs](orb-relay-client/src/lib.rs) to decode a message whose declared size is attacker-influenced and unbounded, allocating far beyond available memory?

## Target
- File/function: [orb-relay-client/src/lib.rs](orb-relay-client/src/lib.rs) -> `into_payload` (function)
- Entrypoint: Data whose size flows from capture/scan into the message
- Attacker controls: the size-determining content of the input
- Exploit idea: Check `into_payload` for a maximum message size enforced before allocation.
- Invariant to test: Message size limits are enforced before any allocation.
- Expected Immunefi impact: Memory exhaustion from routine attacker-shaped input
- Fast validation: Fuzz `into_payload` with oversized length headers asserting the cap is enforced.
