# Q2189: Biometric artifact persisted past its policy by check_aspect_ratio (image/fisheye.rs)

## Question
Can an unprivileged attacker cause `check_aspect_ratio` in [src/image/fisheye.rs](src/image/fisheye.rs) to write captured images/iris data to persistent storage (or leave it there) beyond the consented data policy — via the error path, a retry, or an abort?

## Target
- File/function: [src/image/fisheye.rs](src/image/fisheye.rs) -> `check_aspect_ratio` (function)
- Entrypoint: Aborting or failing a signup after capture
- Attacker controls: the stage at which the failure or abort occurs
- Exploit idea: Check every exit path of `check_aspect_ratio` for deletion/zeroization of persisted biometric artifacts.
- Invariant to test: Captured biometric artifacts are deleted on every exit path unless the policy explicitly permits retention.
- Expected Immunefi impact: Biometric data retained on the device against the user's consent
- Fast validation: Integration test aborting after capture and asserting no residual artifacts remain.
