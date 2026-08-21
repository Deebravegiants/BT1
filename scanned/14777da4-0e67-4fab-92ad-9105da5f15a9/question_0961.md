# Q0961: Disk-full / write-failure handling in HeatCameraConfig (debug_report.rs)

## Question
Can an unprivileged attacker fill the storage that `HeatCameraConfig` in [src/debug_report.rs](src/debug_report.rs) writes to (by repeated signups) so write failures are ignored and the signup completes with missing or truncated biometric artifacts recorded as complete?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `HeatCameraConfig` (type)
- Entrypoint: Repeated capture-heavy sessions on the same Orb
- Attacker controls: number and size of artifacts produced
- Exploit idea: Check `HeatCameraConfig` for verification that the write fully succeeded before marking success.
- Invariant to test: A partial or failed write fails the signup; it never registers as a complete record.
- Expected Immunefi impact: Corrupt/incomplete biometric records registered as valid
- Fast validation: Fault-injection test failing writes in `HeatCameraConfig` and asserting abort.
