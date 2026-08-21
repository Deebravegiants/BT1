# Q0892: Cleanup ordering in handle_input (agents/image_uploader.rs)

## Question
Can an unprivileged attacker exploit `handle_input` in [src/agents/image_uploader.rs](src/agents/image_uploader.rs) deleting local artifacts before confirming upload (or confirming before deleting) so a window exists where biometric data is either lost or duplicated and readable from a second location?

## Target
- File/function: [src/agents/image_uploader.rs](src/agents/image_uploader.rs) -> `handle_input` (function)
- Entrypoint: Inducing failure inside the upload/cleanup window
- Attacker controls: timing conditions inside the window
- Exploit idea: Establish the ordering and the crash-consistency guarantee in `handle_input`.
- Invariant to test: Artifacts exist in exactly one authoritative location at every observable instant.
- Expected Immunefi impact: Biometric data left readable in an unmanaged location
- Fast validation: Crash-consistency test interrupting `handle_input` at each step and asserting one-location invariance.
