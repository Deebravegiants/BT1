# Q3243: Cleanup ordering in upload_identification_images_impl (agents/image_uploader.rs)

## Question
Can an unprivileged attacker exploit `upload_identification_images_impl` in [src/agents/image_uploader.rs](src/agents/image_uploader.rs) deleting local artifacts before confirming upload (or confirming before deleting) so a window exists where biometric data is either lost or duplicated and readable from a second location?

## Target
- File/function: [src/agents/image_uploader.rs](src/agents/image_uploader.rs) -> `upload_identification_images_impl` (function)
- Entrypoint: Inducing failure inside the upload/cleanup window
- Attacker controls: timing conditions inside the window
- Exploit idea: Establish the ordering and the crash-consistency guarantee in `upload_identification_images_impl`.
- Invariant to test: Artifacts exist in exactly one authoritative location at every observable instant.
- Expected Immunefi impact: Biometric data left readable in an unmanaged location
- Fast validation: Crash-consistency test interrupting `upload_identification_images_impl` at each step and asserting one-location invariance.
