# Q1080: Default/permissive initialization in Input (agentwire/port.rs)

## Question
Can an unprivileged attacker benefit from `Input` in [agentwire/src/port.rs](agentwire/src/port.rs) initializing a security-relevant field to a permissive default (checks disabled, policy maximal, mode elevated) that is never overwritten on a reachable path?

## Target
- File/function: [agentwire/src/port.rs](agentwire/src/port.rs) -> `Input` (type)
- Entrypoint: Reaching the path where the default survives to use
- Attacker controls: conditions that prevent the overwrite from occurring
- Exploit idea: Enumerate fields set by `Input` and find one whose overwrite is conditional but whose use is not.
- Invariant to test: Security-relevant fields have no permissive default; absence is an error, not a value.
- Expected Immunefi impact: Signup proceeding with security controls implicitly disabled
- Fast validation: Unit-test `Input` and assert no security field is readable before explicit assignment.
