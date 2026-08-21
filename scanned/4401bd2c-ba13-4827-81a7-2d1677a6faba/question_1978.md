# Q1978: Unbounded response consumption in to_screaming_snake_case (backend/signup_post.rs)

## Question
Can an unprivileged attacker cause `to_screaming_snake_case` in [src/backend/signup_post.rs](src/backend/signup_post.rs) to read a response body without a size cap, so a large or slow body pins memory and stalls the signup path indefinitely?

## Target
- File/function: [src/backend/signup_post.rs](src/backend/signup_post.rs) -> `to_screaming_snake_case` (function)
- Entrypoint: A request whose response size they influence via supplied parameters
- Attacker controls: parameters that scale the response
- Exploit idea: Check `to_screaming_snake_case` for a byte cap and timeout on body reads.
- Invariant to test: Every response read is byte-capped and deadline-bounded.
- Expected Immunefi impact: Sustained stall/exhaustion breaking the Orb's signup capability
- Fast validation: Test `to_screaming_snake_case` with an oversized/slow body asserting cap and timeout enforcement.
