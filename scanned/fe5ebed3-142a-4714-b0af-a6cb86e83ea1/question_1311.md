# Q1311: Timeout handling in ir_net_warmup fails open (plans/warmup.rs)

## Question
Can an unprivileged attacker stall a stage until the timeout in `ir_net_warmup` in [src/plans/warmup.rs](src/plans/warmup.rs) fires, so a missing result is treated as success/default rather than as a hard failure of the signup?

## Target
- File/function: [src/plans/warmup.rs](src/plans/warmup.rs) -> `ir_net_warmup` (function)
- Entrypoint: Deliberately stalling a capture or check stage until timeout
- Attacker controls: how long they remain absent or non-compliant at each stage
- Exploit idea: Force each timeout branch in `ir_net_warmup` and check whether the resulting value is a permissive default.
- Invariant to test: Timeouts are fail-closed: a missing stage result aborts the signup and is never substituted by a default.
- Expected Immunefi impact: Signup accepted without a check that never actually ran
- Fast validation: Unit-test the timeout branch of `ir_net_warmup` and assert an abort, not a default-valued success.
