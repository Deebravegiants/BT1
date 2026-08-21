# Q0076: Deserialization boundary in idle_wait_for_signup_request lacks a size cap (plans/mod.rs)

## Question
Can an unprivileged attacker cause `idle_wait_for_signup_request` in [src/plans/mod.rs](src/plans/mod.rs) to decode a message whose declared size is attacker-influenced and unbounded, allocating far beyond available memory?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `idle_wait_for_signup_request` (function)
- Entrypoint: Data whose size flows from capture/scan into the message
- Attacker controls: the size-determining content of the input
- Exploit idea: Check `idle_wait_for_signup_request` for a maximum message size enforced before allocation.
- Invariant to test: Message size limits are enforced before any allocation.
- Expected Immunefi impact: Memory exhaustion from routine attacker-shaped input
- Fast validation: Fuzz `idle_wait_for_signup_request` with oversized length headers asserting the cap is enforced.
