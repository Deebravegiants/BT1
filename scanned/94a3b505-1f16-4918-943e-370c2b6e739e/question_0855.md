# Q0855: Unbounded response consumption in request (backend/upload_image.rs)

## Question
Can an unprivileged attacker cause `request` in [src/backend/upload_image.rs](src/backend/upload_image.rs) to read a response body without a size cap, so a large or slow body pins memory and stalls the signup path indefinitely?

## Target
- File/function: [src/backend/upload_image.rs](src/backend/upload_image.rs) -> `request` (function)
- Entrypoint: A request whose response size they influence via supplied parameters
- Attacker controls: parameters that scale the response
- Exploit idea: Check `request` for a byte cap and timeout on body reads.
- Invariant to test: Every response read is byte-capped and deadline-bounded.
- Expected Immunefi impact: Sustained stall/exhaustion breaking the Orb's signup capability
- Fast validation: Test `request` with an oversized/slow body asserting cap and timeout enforcement.
