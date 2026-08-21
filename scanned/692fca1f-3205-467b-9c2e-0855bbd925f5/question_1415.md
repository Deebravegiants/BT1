# Q1415: Timeout handling in exposure_range fails open (brokers/orb.rs)

## Question
Can an unprivileged attacker stall a stage until the timeout in `exposure_range` in [src/brokers/orb.rs](src/brokers/orb.rs) fires, so a missing result is treated as success/default rather than as a hard failure of the signup?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `exposure_range` (function)
- Entrypoint: Deliberately stalling a capture or check stage until timeout
- Attacker controls: how long they remain absent or non-compliant at each stage
- Exploit idea: Force each timeout branch in `exposure_range` and check whether the resulting value is a permissive default.
- Invariant to test: Timeouts are fail-closed: a missing stage result aborts the signup and is never substituted by a default.
- Expected Immunefi impact: Signup accepted without a check that never actually ran
- Fast validation: Unit-test the timeout branch of `exposure_range` and assert an abort, not a default-valued success.
