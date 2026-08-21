# Q0276: Default/permissive initialization in init_internal_temperature (brokers/observer.rs)

## Question
Can an unprivileged attacker benefit from `init_internal_temperature` in [src/brokers/observer.rs](src/brokers/observer.rs) initializing a security-relevant field to a permissive default (checks disabled, policy maximal, mode elevated) that is never overwritten on a reachable path?

## Target
- File/function: [src/brokers/observer.rs](src/brokers/observer.rs) -> `init_internal_temperature` (function)
- Entrypoint: Reaching the path where the default survives to use
- Attacker controls: conditions that prevent the overwrite from occurring
- Exploit idea: Enumerate fields set by `init_internal_temperature` and find one whose overwrite is conditional but whose use is not.
- Invariant to test: Security-relevant fields have no permissive default; absence is an error, not a value.
- Expected Immunefi impact: Signup proceeding with security controls implicitly disabled
- Fast validation: Unit-test `init_internal_temperature` and assert no security field is readable before explicit assignment.
