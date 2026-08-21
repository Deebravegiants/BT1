# Q0130: Default/permissive initialization in new (plans/idle.rs)

## Question
Can an unprivileged attacker benefit from `new` in [src/plans/idle.rs](src/plans/idle.rs) initializing a security-relevant field to a permissive default (checks disabled, policy maximal, mode elevated) that is never overwritten on a reachable path?

## Target
- File/function: [src/plans/idle.rs](src/plans/idle.rs) -> `new` (function)
- Entrypoint: Reaching the path where the default survives to use
- Attacker controls: conditions that prevent the overwrite from occurring
- Exploit idea: Enumerate fields set by `new` and find one whose overwrite is conditional but whose use is not.
- Invariant to test: Security-relevant fields have no permissive default; absence is an error, not a value.
- Expected Immunefi impact: Signup proceeding with security controls implicitly disabled
- Fast validation: Unit-test `new` and assert no security field is readable before explicit assignment.
