# Q2332: Abort path in create_tls_config leaves capture state uncleared (orb-relay-client/client.rs)

## Question
Can an unprivileged attacker abort or walk away mid-signup so `create_tls_config` in [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) leaves captured frames, iris data, or the scanned identity in shared state, which the next user's signup then picks up and uploads?

## Target
- File/function: [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) -> `create_tls_config` (function)
- Entrypoint: Starting a signup and abandoning it before completion
- Attacker controls: the exact stage at which the session is abandoned
- Exploit idea: Enumerate the early-return/error paths of `create_tls_config` and check each for a full reset of the shared capture/session state.
- Invariant to test: Every exit path of the signup plan fully resets capture, identity, and fraud state before the next session.
- Expected Immunefi impact: One user's biometric capture attributed to or exposed in another user's signup
- Fast validation: Integration test: abort at each stage, then assert all session state is default before the next run.
