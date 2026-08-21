# Q1165: Timeout handling in ZkpAuth fails open (orb-relay-client/client.rs)

## Question
Can an unprivileged attacker stall a stage until the timeout in `ZkpAuth` in [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) fires, so a missing result is treated as success/default rather than as a hard failure of the signup?

## Target
- File/function: [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) -> `ZkpAuth` (type)
- Entrypoint: Deliberately stalling a capture or check stage until timeout
- Attacker controls: how long they remain absent or non-compliant at each stage
- Exploit idea: Force each timeout branch in `ZkpAuth` and check whether the resulting value is a permissive default.
- Invariant to test: Timeouts are fail-closed: a missing stage result aborts the signup and is never substituted by a default.
- Expected Immunefi impact: Signup accepted without a check that never actually ran
- Fast validation: Unit-test the timeout branch of `ZkpAuth` and assert an abort, not a default-valued success.
