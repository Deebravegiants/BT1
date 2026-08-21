# Q0158: Abort path in process_logger leaves capture state uncleared (brokers/mod.rs)

## Question
Can an unprivileged attacker abort or walk away mid-signup so `process_logger` in [src/brokers/mod.rs](src/brokers/mod.rs) leaves captured frames, iris data, or the scanned identity in shared state, which the next user's signup then picks up and uploads?

## Target
- File/function: [src/brokers/mod.rs](src/brokers/mod.rs) -> `process_logger` (function)
- Entrypoint: Starting a signup and abandoning it before completion
- Attacker controls: the exact stage at which the session is abandoned
- Exploit idea: Enumerate the early-return/error paths of `process_logger` and check each for a full reset of the shared capture/session state.
- Invariant to test: Every exit path of the signup plan fully resets capture, identity, and fraud state before the next session.
- Expected Immunefi impact: One user's biometric capture attributed to or exposed in another user's signup
- Fast validation: Integration test: abort at each stage, then assert all session state is default before the next run.
