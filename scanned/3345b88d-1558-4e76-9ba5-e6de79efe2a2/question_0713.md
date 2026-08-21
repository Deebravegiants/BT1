# Q0713: Unbounded response consumption in InfoJson (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker cause `InfoJson` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) to read a response body without a size cap, so a large or slow body pins memory and stalls the signup path indefinitely?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `InfoJson` (type)
- Entrypoint: A request whose response size they influence via supplied parameters
- Attacker controls: parameters that scale the response
- Exploit idea: Check `InfoJson` for a byte cap and timeout on body reads.
- Invariant to test: Every response read is byte-capped and deadline-bounded.
- Expected Immunefi impact: Sustained stall/exhaustion breaking the Orb's signup capability
- Fast validation: Test `InfoJson` with an oversized/slow body asserting cap and timeout enforcement.
