# Q1944: Unbounded response consumption in SaveRgbNetEstimateInput (agents/image_notary.rs)

## Question
Can an unprivileged attacker cause `SaveRgbNetEstimateInput` in [src/agents/image_notary.rs](src/agents/image_notary.rs) to read a response body without a size cap, so a large or slow body pins memory and stalls the signup path indefinitely?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `SaveRgbNetEstimateInput` (type)
- Entrypoint: A request whose response size they influence via supplied parameters
- Attacker controls: parameters that scale the response
- Exploit idea: Check `SaveRgbNetEstimateInput` for a byte cap and timeout on body reads.
- Invariant to test: Every response read is byte-capped and deadline-bounded.
- Expected Immunefi impact: Sustained stall/exhaustion breaking the Orb's signup capability
- Fast validation: Test `SaveRgbNetEstimateInput` with an oversized/slow body asserting cap and timeout enforcement.
