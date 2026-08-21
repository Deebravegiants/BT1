# Q3641: Abort path in Status leaves capture state uncleared (plans/enroll_user.rs)

## Question
Can an unprivileged attacker abort or walk away mid-signup so `Status` in [src/plans/enroll_user.rs](src/plans/enroll_user.rs) leaves captured frames, iris data, or the scanned identity in shared state, which the next user's signup then picks up and uploads?

## Target
- File/function: [src/plans/enroll_user.rs](src/plans/enroll_user.rs) -> `Status` (type)
- Entrypoint: Starting a signup and abandoning it before completion
- Attacker controls: the exact stage at which the session is abandoned
- Exploit idea: Enumerate the early-return/error paths of `Status` and check each for a full reset of the shared capture/session state.
- Invariant to test: Every exit path of the signup plan fully resets capture, identity, and fraud state before the next session.
- Expected Immunefi impact: One user's biometric capture attributed to or exposed in another user's signup
- Fast validation: Integration test: abort at each stage, then assert all session state is default before the next run.
