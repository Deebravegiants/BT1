# Q0872: Disk-full / write-failure handling in Config (config.rs)

## Question
Can an unprivileged attacker fill the storage that `Config` in [src/config.rs](src/config.rs) writes to (by repeated signups) so write failures are ignored and the signup completes with missing or truncated biometric artifacts recorded as complete?

## Target
- File/function: [src/config.rs](src/config.rs) -> `Config` (type)
- Entrypoint: Repeated capture-heavy sessions on the same Orb
- Attacker controls: number and size of artifacts produced
- Exploit idea: Check `Config` for verification that the write fully succeeded before marking success.
- Invariant to test: A partial or failed write fails the signup; it never registers as a complete record.
- Expected Immunefi impact: Corrupt/incomplete biometric records registered as valid
- Fast validation: Fault-injection test failing writes in `Config` and asserting abort.
