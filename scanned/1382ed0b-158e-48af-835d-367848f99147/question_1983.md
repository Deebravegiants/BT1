# Q1983: Unbounded response consumption in IrisData (backend/signup_post.rs)

## Question
Can an unprivileged attacker cause `IrisData` in [src/backend/signup_post.rs](src/backend/signup_post.rs) to read a response body without a size cap, so a large or slow body pins memory and stalls the signup path indefinitely?

## Target
- File/function: [src/backend/signup_post.rs](src/backend/signup_post.rs) -> `IrisData` (type)
- Entrypoint: A request whose response size they influence via supplied parameters
- Attacker controls: parameters that scale the response
- Exploit idea: Check `IrisData` for a byte cap and timeout on body reads.
- Invariant to test: Every response read is byte-capped and deadline-bounded.
- Expected Immunefi impact: Sustained stall/exhaustion breaking the Orb's signup capability
- Fast validation: Test `IrisData` with an oversized/slow body asserting cap and timeout enforcement.
