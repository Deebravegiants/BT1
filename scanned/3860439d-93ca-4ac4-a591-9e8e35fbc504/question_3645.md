# Q3645: Timeout handling in poll_extra fails open (plans/idle.rs)

## Question
Can an unprivileged attacker stall a stage until the timeout in `poll_extra` in [src/plans/idle.rs](src/plans/idle.rs) fires, so a missing result is treated as success/default rather than as a hard failure of the signup?

## Target
- File/function: [src/plans/idle.rs](src/plans/idle.rs) -> `poll_extra` (function)
- Entrypoint: Deliberately stalling a capture or check stage until timeout
- Attacker controls: how long they remain absent or non-compliant at each stage
- Exploit idea: Force each timeout branch in `poll_extra` and check whether the resulting value is a permissive default.
- Invariant to test: Timeouts are fail-closed: a missing stage result aborts the signup and is never substituted by a default.
- Expected Immunefi impact: Signup accepted without a check that never actually ran
- Fast validation: Unit-test the timeout branch of `poll_extra` and assert an abort, not a default-valued success.
