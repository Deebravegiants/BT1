# Q3722: Default/permissive initialization in start_image_notary (brokers/orb.rs)

## Question
Can an unprivileged attacker benefit from `start_image_notary` in [src/brokers/orb.rs](src/brokers/orb.rs) initializing a security-relevant field to a permissive default (checks disabled, policy maximal, mode elevated) that is never overwritten on a reachable path?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `start_image_notary` (function)
- Entrypoint: Reaching the path where the default survives to use
- Attacker controls: conditions that prevent the overwrite from occurring
- Exploit idea: Enumerate fields set by `start_image_notary` and find one whose overwrite is conditional but whose use is not.
- Invariant to test: Security-relevant fields have no permissive default; absence is an error, not a value.
- Expected Immunefi impact: Signup proceeding with security controls implicitly disabled
- Fast validation: Unit-test `start_image_notary` and assert no security field is readable before explicit assignment.
