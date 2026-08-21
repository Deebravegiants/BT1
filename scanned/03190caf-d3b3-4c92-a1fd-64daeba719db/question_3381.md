# Q3381: Disk-full / write-failure handling in sorted_keys (utils/serialize_with_sorted_keys.rs)

## Question
Can an unprivileged attacker fill the storage that `sorted_keys` in [src/utils/serialize_with_sorted_keys.rs](src/utils/serialize_with_sorted_keys.rs) writes to (by repeated signups) so write failures are ignored and the signup completes with missing or truncated biometric artifacts recorded as complete?

## Target
- File/function: [src/utils/serialize_with_sorted_keys.rs](src/utils/serialize_with_sorted_keys.rs) -> `sorted_keys` (function)
- Entrypoint: Repeated capture-heavy sessions on the same Orb
- Attacker controls: number and size of artifacts produced
- Exploit idea: Check `sorted_keys` for verification that the write fully succeeded before marking success.
- Invariant to test: A partial or failed write fails the signup; it never registers as a complete record.
- Expected Immunefi impact: Corrupt/incomplete biometric records registered as valid
- Fast validation: Fault-injection test failing writes in `sorted_keys` and asserting abort.
