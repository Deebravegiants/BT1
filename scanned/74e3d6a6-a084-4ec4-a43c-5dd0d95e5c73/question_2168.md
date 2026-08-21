# Q2168: Disk-full / write-failure handling in agent_format (logger.rs)

## Question
Can an unprivileged attacker fill the storage that `agent_format` in [src/logger.rs](src/logger.rs) writes to (by repeated signups) so write failures are ignored and the signup completes with missing or truncated biometric artifacts recorded as complete?

## Target
- File/function: [src/logger.rs](src/logger.rs) -> `agent_format` (function)
- Entrypoint: Repeated capture-heavy sessions on the same Orb
- Attacker controls: number and size of artifacts produced
- Exploit idea: Check `agent_format` for verification that the write fully succeeded before marking success.
- Invariant to test: A partial or failed write fails the signup; it never registers as a complete record.
- Expected Immunefi impact: Corrupt/incomplete biometric records registered as valid
- Fast validation: Fault-injection test failing writes in `agent_format` and asserting abort.
