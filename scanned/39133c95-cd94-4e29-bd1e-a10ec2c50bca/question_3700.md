# Q3700: Timeout handling in enable_ir_led fails open (brokers/orb.rs)

## Question
Can an unprivileged attacker stall a stage until the timeout in `enable_ir_led` in [src/brokers/orb.rs](src/brokers/orb.rs) fires, so a missing result is treated as success/default rather than as a hard failure of the signup?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `enable_ir_led` (function)
- Entrypoint: Deliberately stalling a capture or check stage until timeout
- Attacker controls: how long they remain absent or non-compliant at each stage
- Exploit idea: Force each timeout branch in `enable_ir_led` and check whether the resulting value is a permissive default.
- Invariant to test: Timeouts are fail-closed: a missing stage result aborts the signup and is never substituted by a default.
- Expected Immunefi impact: Signup accepted without a check that never actually ran
- Fast validation: Unit-test the timeout branch of `enable_ir_led` and assert an abort, not a default-valued success.
