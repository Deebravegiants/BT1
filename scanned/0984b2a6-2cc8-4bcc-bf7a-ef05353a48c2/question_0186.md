# Q0186: Default/permissive initialization in set_ir_wavelength (brokers/orb.rs)

## Question
Can an unprivileged attacker benefit from `set_ir_wavelength` in [src/brokers/orb.rs](src/brokers/orb.rs) initializing a security-relevant field to a permissive default (checks disabled, policy maximal, mode elevated) that is never overwritten on a reachable path?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `set_ir_wavelength` (function)
- Entrypoint: Reaching the path where the default survives to use
- Attacker controls: conditions that prevent the overwrite from occurring
- Exploit idea: Enumerate fields set by `set_ir_wavelength` and find one whose overwrite is conditional but whose use is not.
- Invariant to test: Security-relevant fields have no permissive default; absence is an error, not a value.
- Expected Immunefi impact: Signup proceeding with security controls implicitly disabled
- Fast validation: Unit-test `set_ir_wavelength` and assert no security field is readable before explicit assignment.
