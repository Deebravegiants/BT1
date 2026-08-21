# Q3186: Unbounded response consumption in Ssd (backend/status.rs)

## Question
Can an unprivileged attacker cause `Ssd` in [src/backend/status.rs](src/backend/status.rs) to read a response body without a size cap, so a large or slow body pins memory and stalls the signup path indefinitely?

## Target
- File/function: [src/backend/status.rs](src/backend/status.rs) -> `Ssd` (type)
- Entrypoint: A request whose response size they influence via supplied parameters
- Attacker controls: parameters that scale the response
- Exploit idea: Check `Ssd` for a byte cap and timeout on body reads.
- Invariant to test: Every response read is byte-capped and deadline-bounded.
- Expected Immunefi impact: Sustained stall/exhaustion breaking the Orb's signup capability
- Fast validation: Test `Ssd` with an oversized/slow body asserting cap and timeout enforcement.
