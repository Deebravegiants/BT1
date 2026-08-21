# Q0071: Timeout handling in operator_qr_code fails open (plans/mod.rs)

## Question
Can an unprivileged attacker stall a stage until the timeout in `operator_qr_code` in [src/plans/mod.rs](src/plans/mod.rs) fires, so a missing result is treated as success/default rather than as a hard failure of the signup?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `operator_qr_code` (function)
- Entrypoint: Deliberately stalling a capture or check stage until timeout
- Attacker controls: how long they remain absent or non-compliant at each stage
- Exploit idea: Force each timeout branch in `operator_qr_code` and check whether the resulting value is a permissive default.
- Invariant to test: Timeouts are fail-closed: a missing stage result aborts the signup and is never substituted by a default.
- Expected Immunefi impact: Signup accepted without a check that never actually ran
- Fast validation: Unit-test the timeout branch of `operator_qr_code` and assert an abort, not a default-valued success.
