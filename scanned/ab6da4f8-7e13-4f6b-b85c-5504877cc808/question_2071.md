# Q2071: Disk-full / write-failure handling in upload_identification_images_impl (agents/image_uploader.rs)

## Question
Can an unprivileged attacker fill the storage that `upload_identification_images_impl` in [src/agents/image_uploader.rs](src/agents/image_uploader.rs) writes to (by repeated signups) so write failures are ignored and the signup completes with missing or truncated biometric artifacts recorded as complete?

## Target
- File/function: [src/agents/image_uploader.rs](src/agents/image_uploader.rs) -> `upload_identification_images_impl` (function)
- Entrypoint: Repeated capture-heavy sessions on the same Orb
- Attacker controls: number and size of artifacts produced
- Exploit idea: Check `upload_identification_images_impl` for verification that the write fully succeeded before marking success.
- Invariant to test: A partial or failed write fails the signup; it never registers as a complete record.
- Expected Immunefi impact: Corrupt/incomplete biometric records registered as valid
- Fast validation: Fault-injection test failing writes in `upload_identification_images_impl` and asserting abort.
