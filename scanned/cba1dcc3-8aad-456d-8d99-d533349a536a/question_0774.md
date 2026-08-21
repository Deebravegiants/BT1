# Q0774: Unbounded response consumption in SaveThermalDataInput (agents/image_notary.rs)

## Question
Can an unprivileged attacker cause `SaveThermalDataInput` in [src/agents/image_notary.rs](src/agents/image_notary.rs) to read a response body without a size cap, so a large or slow body pins memory and stalls the signup path indefinitely?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `SaveThermalDataInput` (type)
- Entrypoint: A request whose response size they influence via supplied parameters
- Attacker controls: parameters that scale the response
- Exploit idea: Check `SaveThermalDataInput` for a byte cap and timeout on body reads.
- Invariant to test: Every response read is byte-capped and deadline-bounded.
- Expected Immunefi impact: Sustained stall/exhaustion breaking the Orb's signup capability
- Fast validation: Test `SaveThermalDataInput` with an oversized/slow body asserting cap and timeout enforcement.
