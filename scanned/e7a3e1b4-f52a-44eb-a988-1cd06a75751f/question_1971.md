# Q1971: Unbounded response consumption in Config (backend/config.rs)

## Question
Can an unprivileged attacker cause `Config` in [src/backend/config.rs](src/backend/config.rs) to read a response body without a size cap, so a large or slow body pins memory and stalls the signup path indefinitely?

## Target
- File/function: [src/backend/config.rs](src/backend/config.rs) -> `Config` (type)
- Entrypoint: A request whose response size they influence via supplied parameters
- Attacker controls: parameters that scale the response
- Exploit idea: Check `Config` for a byte cap and timeout on body reads.
- Invariant to test: Every response read is byte-capped and deadline-bounded.
- Expected Immunefi impact: Sustained stall/exhaustion breaking the Orb's signup capability
- Fast validation: Test `Config` with an oversized/slow body asserting cap and timeout enforcement.
