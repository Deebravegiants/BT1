# Q3719: Deserialization boundary in start_ir_auto_exposure lacks a size cap (brokers/orb.rs)

## Question
Can an unprivileged attacker cause `start_ir_auto_exposure` in [src/brokers/orb.rs](src/brokers/orb.rs) to decode a message whose declared size is attacker-influenced and unbounded, allocating far beyond available memory?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `start_ir_auto_exposure` (function)
- Entrypoint: Data whose size flows from capture/scan into the message
- Attacker controls: the size-determining content of the input
- Exploit idea: Check `start_ir_auto_exposure` for a maximum message size enforced before allocation.
- Invariant to test: Message size limits are enforced before any allocation.
- Expected Immunefi impact: Memory exhaustion from routine attacker-shaped input
- Fast validation: Fuzz `start_ir_auto_exposure` with oversized length headers asserting the cap is enforced.
