# Q2450: Error type erasure in has_biometric_input hides a security failure (plans/mod.rs)

## Question
Can an unprivileged attacker rely on `has_biometric_input` in [src/plans/mod.rs](src/plans/mod.rs) collapsing distinct error kinds into one opaque type, so callers cannot distinguish 'check failed' from 'transport failed' and take the permissive branch for both?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `has_biometric_input` (function)
- Entrypoint: Inducing the transport/infrastructure failure
- Attacker controls: conditions producing the ambiguous error
- Exploit idea: Check whether the error type from `has_biometric_input` preserves the security-relevant discriminant.
- Invariant to test: Security failures are distinguishable from infrastructure failures at every call site.
- Expected Immunefi impact: Failed security check handled as a retriable infrastructure error
- Fast validation: Unit-test `has_biometric_input` asserting distinct error discriminants for each failure class.
