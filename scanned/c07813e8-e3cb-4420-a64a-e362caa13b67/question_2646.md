# Q2646: Timeout handling in async_main fails open (lib.rs)

## Question
Can an unprivileged attacker stall a stage until the timeout in `async_main` in [src/lib.rs](src/lib.rs) fires, so a missing result is treated as success/default rather than as a hard failure of the signup?

## Target
- File/function: [src/lib.rs](src/lib.rs) -> `async_main` (function)
- Entrypoint: Deliberately stalling a capture or check stage until timeout
- Attacker controls: how long they remain absent or non-compliant at each stage
- Exploit idea: Force each timeout branch in `async_main` and check whether the resulting value is a permissive default.
- Invariant to test: Timeouts are fail-closed: a missing stage result aborts the signup and is never substituted by a default.
- Expected Immunefi impact: Signup accepted without a check that never actually ran
- Fast validation: Unit-test the timeout branch of `async_main` and assert an abort, not a default-valued success.
