# Q1989: Unbounded response consumption in Response (backend/signup_poll.rs)

## Question
Can an unprivileged attacker cause `Response` in [src/backend/signup_poll.rs](src/backend/signup_poll.rs) to read a response body without a size cap, so a large or slow body pins memory and stalls the signup path indefinitely?

## Target
- File/function: [src/backend/signup_poll.rs](src/backend/signup_poll.rs) -> `Response` (type)
- Entrypoint: A request whose response size they influence via supplied parameters
- Attacker controls: parameters that scale the response
- Exploit idea: Check `Response` for a byte cap and timeout on body reads.
- Invariant to test: Every response read is byte-capped and deadline-bounded.
- Expected Immunefi impact: Sustained stall/exhaustion breaking the Orb's signup capability
- Fast validation: Test `Response` with an oversized/slow body asserting cap and timeout enforcement.
