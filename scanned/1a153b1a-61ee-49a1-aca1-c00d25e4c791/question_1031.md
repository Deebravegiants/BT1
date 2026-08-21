# Q1031: Disk-full / write-failure handling in as_ndarray (utils/rkyv_ndarray.rs)

## Question
Can an unprivileged attacker fill the storage that `as_ndarray` in [src/utils/rkyv_ndarray.rs](src/utils/rkyv_ndarray.rs) writes to (by repeated signups) so write failures are ignored and the signup completes with missing or truncated biometric artifacts recorded as complete?

## Target
- File/function: [src/utils/rkyv_ndarray.rs](src/utils/rkyv_ndarray.rs) -> `as_ndarray` (function)
- Entrypoint: Repeated capture-heavy sessions on the same Orb
- Attacker controls: number and size of artifacts produced
- Exploit idea: Check `as_ndarray` for verification that the write fully succeeded before marking success.
- Invariant to test: A partial or failed write fails the signup; it never registers as a complete record.
- Expected Immunefi impact: Corrupt/incomplete biometric records registered as valid
- Fast validation: Fault-injection test failing writes in `as_ndarray` and asserting abort.
