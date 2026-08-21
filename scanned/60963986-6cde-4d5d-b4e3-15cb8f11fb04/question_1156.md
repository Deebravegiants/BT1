# Q1156: Default/permissive initialization in reconnect (orb-relay-client/client.rs)

## Question
Can an unprivileged attacker benefit from `reconnect` in [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) initializing a security-relevant field to a permissive default (checks disabled, policy maximal, mode elevated) that is never overwritten on a reachable path?

## Target
- File/function: [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) -> `reconnect` (function)
- Entrypoint: Reaching the path where the default survives to use
- Attacker controls: conditions that prevent the overwrite from occurring
- Exploit idea: Enumerate fields set by `reconnect` and find one whose overwrite is conditional but whose use is not.
- Invariant to test: Security-relevant fields have no permissive default; absence is an error, not a value.
- Expected Immunefi impact: Signup proceeding with security controls implicitly disabled
- Fast validation: Unit-test `reconnect` and assert no security field is readable before explicit assignment.
