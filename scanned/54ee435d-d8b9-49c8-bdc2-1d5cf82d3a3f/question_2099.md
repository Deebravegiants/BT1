# Q2099: Biometric artifact persisted past its policy by image_notary_history (debug_report.rs)

## Question
Can an unprivileged attacker cause `image_notary_history` in [src/debug_report.rs](src/debug_report.rs) to write captured images/iris data to persistent storage (or leave it there) beyond the consented data policy — via the error path, a retry, or an abort?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `image_notary_history` (function)
- Entrypoint: Aborting or failing a signup after capture
- Attacker controls: the stage at which the failure or abort occurs
- Exploit idea: Check every exit path of `image_notary_history` for deletion/zeroization of persisted biometric artifacts.
- Invariant to test: Captured biometric artifacts are deleted on every exit path unless the policy explicitly permits retention.
- Expected Immunefi impact: Biometric data retained on the device against the user's consent
- Fast validation: Integration test aborting after capture and asserting no residual artifacts remain.
