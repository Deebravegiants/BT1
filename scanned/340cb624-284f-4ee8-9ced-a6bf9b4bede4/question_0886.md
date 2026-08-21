# Q0886: Disk-full / write-failure handling in wait_queues (agents/data_uploader.rs)

## Question
Can an unprivileged attacker fill the storage that `wait_queues` in [src/agents/data_uploader.rs](src/agents/data_uploader.rs) writes to (by repeated signups) so write failures are ignored and the signup completes with missing or truncated biometric artifacts recorded as complete?

## Target
- File/function: [src/agents/data_uploader.rs](src/agents/data_uploader.rs) -> `wait_queues` (function)
- Entrypoint: Repeated capture-heavy sessions on the same Orb
- Attacker controls: number and size of artifacts produced
- Exploit idea: Check `wait_queues` for verification that the write fully succeeded before marking success.
- Invariant to test: A partial or failed write fails the signup; it never registers as a complete record.
- Expected Immunefi impact: Corrupt/incomplete biometric records registered as valid
- Fast validation: Fault-injection test failing writes in `wait_queues` and asserting abort.
