# Q3353: Biometric artifact persisted past its policy by new_with_keep_fds (process.rs)

## Question
Can an unprivileged attacker cause `new_with_keep_fds` in [src/process.rs](src/process.rs) to write captured images/iris data to persistent storage (or leave it there) beyond the consented data policy — via the error path, a retry, or an abort?

## Target
- File/function: [src/process.rs](src/process.rs) -> `new_with_keep_fds` (function)
- Entrypoint: Aborting or failing a signup after capture
- Attacker controls: the stage at which the failure or abort occurs
- Exploit idea: Check every exit path of `new_with_keep_fds` for deletion/zeroization of persisted biometric artifacts.
- Invariant to test: Captured biometric artifacts are deleted on every exit path unless the policy explicitly permits retention.
- Expected Immunefi impact: Biometric data retained on the device against the user's consent
- Fast validation: Integration test aborting after capture and asserting no residual artifacts remain.
