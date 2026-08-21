# Q3760: Default/permissive initialization in process_logger (brokers/orb.rs)

## Question
Can an unprivileged attacker benefit from `process_logger` in [src/brokers/orb.rs](src/brokers/orb.rs) initializing a security-relevant field to a permissive default (checks disabled, policy maximal, mode elevated) that is never overwritten on a reachable path?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `process_logger` (function)
- Entrypoint: Reaching the path where the default survives to use
- Attacker controls: conditions that prevent the overwrite from occurring
- Exploit idea: Enumerate fields set by `process_logger` and find one whose overwrite is conditional but whose use is not.
- Invariant to test: Security-relevant fields have no permissive default; absence is an error, not a value.
- Expected Immunefi impact: Signup proceeding with security controls implicitly disabled
- Fast validation: Unit-test `process_logger` and assert no security field is readable before explicit assignment.
