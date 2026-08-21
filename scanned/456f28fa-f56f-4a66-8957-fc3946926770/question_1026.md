# Q1026: Disk-full / write-failure handling in set_proc_name (utils/mod.rs)

## Question
Can an unprivileged attacker fill the storage that `set_proc_name` in [src/utils/mod.rs](src/utils/mod.rs) writes to (by repeated signups) so write failures are ignored and the signup completes with missing or truncated biometric artifacts recorded as complete?

## Target
- File/function: [src/utils/mod.rs](src/utils/mod.rs) -> `set_proc_name` (function)
- Entrypoint: Repeated capture-heavy sessions on the same Orb
- Attacker controls: number and size of artifacts produced
- Exploit idea: Check `set_proc_name` for verification that the write fully succeeded before marking success.
- Invariant to test: A partial or failed write fails the signup; it never registers as a complete record.
- Expected Immunefi impact: Corrupt/incomplete biometric records registered as valid
- Fast validation: Fault-injection test failing writes in `set_proc_name` and asserting abort.
