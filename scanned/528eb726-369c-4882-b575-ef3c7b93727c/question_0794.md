# Q0794: Unbounded response consumption in client (backend/mod.rs)

## Question
Can an unprivileged attacker cause `client` in [src/backend/mod.rs](src/backend/mod.rs) to read a response body without a size cap, so a large or slow body pins memory and stalls the signup path indefinitely?

## Target
- File/function: [src/backend/mod.rs](src/backend/mod.rs) -> `client` (function)
- Entrypoint: A request whose response size they influence via supplied parameters
- Attacker controls: parameters that scale the response
- Exploit idea: Check `client` for a byte cap and timeout on body reads.
- Invariant to test: Every response read is byte-capped and deadline-bounded.
- Expected Immunefi impact: Sustained stall/exhaustion breaking the Orb's signup capability
- Fast validation: Test `client` with an oversized/slow body asserting cap and timeout enforcement.
